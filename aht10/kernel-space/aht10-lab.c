#include <linux/bitops.h>
#include <linux/delay.h>
#include <linux/hwmon.h>
#include <linux/i2c.h>
#include <linux/jiffies.h>
#include <linux/kernel.h>
#include <linux/math64.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/slab.h>

#define AHT10_DRIVER_NAME "aht10-lab"
#define AHT10_I2C_ADDR 0x38

/* AHT10 commands */
#define AHT10_CMD_INIT       0xBE
#define AHT10_CMD_TRIGGER    0xAC
#define AHT10_CMD_SOFT_RESET 0xBA

/* AHT10 status bits */
#define AHT10_STATUS_BUSY       BIT(7)
#define AHT10_STATUS_CALIBRATED BIT(3)

#define AHT10_PAYLOAD_SIZE       6
#define AHT10_UPDATE_INTERVAL_MS 1000

struct aht10_data {
    struct i2c_client *client;
    struct mutex lock;

    long temp_milli_c;
    long hum_milli_percent;

    unsigned long last_update;
    bool valid;
};

/* --------------------------------------------------------------------------
 * Sensor I/O helpers
 * -------------------------------------------------------------------------- */
static int aht10_init(struct i2c_client *client)
{
    u8 cmd[] = { AHT10_CMD_INIT, 0x08, 0x00 };
    int ret;

    ret = i2c_master_send(client, cmd, sizeof(cmd));
    if (ret != sizeof(cmd)) {
        dev_err(&client->dev, "failed to send init command: ret = %d\n", ret);
        return ret < 0 ? ret : -EIO;
    }

    msleep(20);
    dev_info(&client->dev, "sensor initialization command sent\n");

    return 0;
}

static int aht10_soft_reset(struct i2c_client *client)
{
    u8 cmd = AHT10_CMD_SOFT_RESET;
    int ret;

    ret = i2c_master_send(client, &cmd, 1);
    if (ret != 1) {
        dev_err(&client->dev, "failed to send soft reset: ret=%d\n", ret);
        return ret < 0 ? ret : -EIO;
    }

    msleep(20);
    return 0;
}

static int aht10_read_measurement(struct i2c_client *client,
                                  int *temp_milli_c,
                                  int *hum_milli_percent)
{
    u8 cmd[] = { AHT10_CMD_TRIGGER, 0x33, 0x00 };
    u8 buf[AHT10_PAYLOAD_SIZE];
    u32 humidity_raw;
    u32 temperature_raw;
    u64 value;
    int ret;

    ret = i2c_master_send(client, cmd, sizeof(cmd));
    if (ret != sizeof(cmd)) {
        dev_err(&client->dev, "failed to send trigger command: ret = %d\n", ret);
        return ret < 0 ? ret : -EIO;
    }

    /* Datasheet requires more than 75 ms after triggering measurement. */
    msleep(80);

    ret = i2c_master_recv(client, buf, sizeof(buf));
    if (ret != sizeof(buf)) {
        dev_err(&client->dev, "failed to read measurement payload: ret = %d\n", ret);
        return ret < 0 ? ret : -EIO;
    }

    dev_dbg(&client->dev,
             "raw payload: %02x %02x %02x %02x %02x %02x\n",
             buf[0], buf[1], buf[2], buf[3], buf[4], buf[5]);

    if (buf[0] & AHT10_STATUS_BUSY) {
        dev_err(&client->dev, "sensor still busy!\n");
        return -EBUSY;
    }

    if (!(buf[0] & AHT10_STATUS_CALIBRATED)) {
        dev_warn(&client->dev, "sensor calibration bit is not set!\n");
    }

    humidity_raw = ((u32)buf[1] << 12) |
                   ((u32)buf[2] << 4)  |
                   ((u32)buf[3] >> 4);

    temperature_raw = (((u32)buf[3] & 0x0F) << 16) |
                      ((u32)buf[4] << 8)           |
                      ((u32)buf[5]);

    /*
     * Humidity formula:
     * RH = humidity_raw * 100 / 2^20
     *
     * We store it as milli-percent:
     * 45.678 %RH -> 45678
     */
    value = (u64)humidity_raw * 100000;
    *hum_milli_percent = div_u64(value, 1 << 20);

    /*
     * Temperature formula:
     * T = temperature_raw * 200 / 2^20 - 50
     *
     * We store it as milli-percent:
     * 23.456 C -> 23456
     */
    value = (u64)temperature_raw * 200000;
    *temp_milli_c = div_u64(value, 1 << 20) - 50000;

    if (*hum_milli_percent < 0 || *hum_milli_percent > 100000) {
        dev_err(&client->dev, "invalid humidity: %d milli-percent\n",
                *hum_milli_percent);
        return -ERANGE;
    }

    if (*temp_milli_c < -40000 || *temp_milli_c > 85000) {
        dev_err(&client->dev, "invalid temperature: %d milli-percent\n",
                *temp_milli_c);
        return -ERANGE;
    }

    return 0;
}

static int aht10_update_measurement(struct aht10_data* data)
{
    int temp;
    int hum;
    int ret;

    if (data->valid && time_before(jiffies, data->last_update + msecs_to_jiffies(AHT10_UPDATE_INTERVAL_MS))) {
        return 0;
    }

    ret = aht10_read_measurement(data->client, &temp, &hum);
    if (ret) {
        return ret;
    }

    data->temp_milli_c = temp;
    data->hum_milli_percent = hum;
    data->last_update = jiffies;
    data->valid = true;
    
    return 0;
}

/* --------------------------------------------------------------------------
 * HWMON integration
 * -------------------------------------------------------------------------- */
static const struct hwmon_channel_info *const aht10_hwmon_info[] = {
    HWMON_CHANNEL_INFO(temp, HWMON_T_INPUT),
    HWMON_CHANNEL_INFO(humidity, HWMON_T_INPUT),
    NULL
};

static umode_t aht10_hwmon_is_visible(const void *drvdata,
                                      enum hwmon_sensor_types type,
                                      u32 attr,
                                      int channel)
{
    switch (type) {
    case hwmon_temp_input:
        if (attr == hwmon_temp_input)
            return 0444;
        break;
    case hwmon_humidity:
        if (attr == hwmon_humidity_input)
            return 0444;
        break;
    default:
        break;
    }

    return 0;
}

static int aht10_hwmon_read(struct device *dev,
                            enum hwmon_sensor_types type,
                            u32 attr,
                            int channel,
                            long *val)
{
    struct aht10_data *data = dev_get_drvdata(dev);
    int ret;

    mutex_lock(&data->lock);

    ret = aht10_update_measurement(data);
    if (ret)
        goto out_unlock;

    switch (type) {
    case hwmon_temp_input:
        if (attr != hwmon_temp_input) {
            ret = -EOPNOTSUPP;
            goto out_unlock;
        }
        *val = data->temp_milli_c;
        ret = 0;
        break;

    case hwmon_humidity:
        if (attr != hwmon_humidity_input) {
            ret = -EOPNOTSUPP;
            goto out_unlock;
        }
        *val = data->hum_milli_percent;
        ret = 0;
        break;

    default:
        ret = -EOPNOTSUPP;
        break;
    }

out_unlock:
    mutex_unlock(&data->lock);
    return ret;
}

static const struct hwmon_ops aht10_hwmon_ops = {
    .is_visible = aht10_hwmon_is_visible,
    .read = aht10_hwmon_read,
};

static const struct hwmon_chip_info aht10_chip_info = {
    .ops = &aht10_hwmon_ops,
    .info = aht10_hwmon_info,
};

/* --------------------------------------------------------------------------
 * I2C driver lifecycle
 * -------------------------------------------------------------------------- */
static int aht10_probe(struct i2c_client *client)
{
    struct i2c_adapter *adapter = client->adapter;
    struct aht10_data *data;
    struct device *hwmon_dev;
    int ret;

    dev_info(&client->dev, "aht10_probe called: addr=0x%02x\n", client->addr);

    if (!i2c_check_functionality(adapter, I2C_FUNC_I2C)) {
        dev_err(&client->dev,
                "I2C adapter does not support plain I2C transfers!\n");
        return -EOPNOTSUPP;
    }

    if (client->addr != AHT10_I2C_ADDR) {
        dev_warn(&client->dev,
                 "unexpected I2C address 0x%02x, expected 0x%02x\n",
                 client->addr, AHT10_I2C_ADDR);
    }

    data = devm_kzalloc(&client->dev, sizeof(*data), GFP_KERNEL);
    if (!data)
        return -ENOMEM;

    data->client = client;
    mutex_init(&data->lock);

    i2c_set_clientdata(client, data);

    msleep(20);

    ret = aht10_init(client);
    if (ret)
        return ret;

    hwmon_dev = devm_hwmon_device_register_with_info(&client->dev,
                                                     "aht10_lab",
                                                     data,
                                                     &aht10_chip_info,
                                                     NULL);
    if (IS_ERR(hwmon_dev)) {
        dev_err(&client->dev,
                "failed to register hwmon service: %ld\n",
                PTR_ERR(hwmon_dev));
        return PTR_ERR(hwmon_dev);
    }

    dev_info(&client->dev, "hwmon device registered succesfully\n");
    dev_info(&client->dev, "AHT10 driver bound successfully!\n");

    return 0;
}

static void aht10_remove(struct i2c_client *client)
{
    dev_info(&client->dev, "AHT10 driver removed!");
}

/* --------------------------------------------------------------------------
 * I2C driver registration
 * -------------------------------------------------------------------------- */
static const struct i2c_device_id aht10_id[] = {
    { "aht10-lab", 0 },
    { "aht10", 0 },
    { }
};
MODULE_DEVICE_TABLE(i2c, aht10_id);

static const struct of_device_id aht10_of_match[] = {
    { .compatible = "learning,aht10-lab" },
    { .compatible = "aosong,aht10" },
    { }
};
MODULE_DEVICE_TABLE(of, aht10_of_match);

static struct i2c_driver aht10_driver = {
    .driver = {
        .name = AHT10_DRIVER_NAME,
        .of_match_table = aht10_of_match,
    },
    .id_table = aht10_id,
    .probe = aht10_probe,
    .remove = aht10_remove,
};

module_i2c_driver(aht10_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Dakata99");
MODULE_DESCRIPTION("Kernel driver for AHT10 - temperature and humidity sensor.");
MODULE_VERSION("1.0");
