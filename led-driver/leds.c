// leds.c

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/of.h>

#define DEVICE_NAME "pi_led"
#define LED_COUNT 3

struct pi_led_data {
    struct gpio_desc *leds[LED_COUNT];
    struct miscdevice miscdev;
    char state[4]; /* "000\n" */
};

static void pi_led_apply_pattern(struct pi_led_data *data, const char *pattern)
{
    /*
     * User pattern:
     *
     * "001" -> LED1 on
     * "010" -> LED2 on
     * "100" -> LED3 on
     *
     * data->leds[0] = LED1
     * data->leds[1] = LED2
     * data->leds[2] = LED3
     */

    gpiod_set_value_cansleep(data->leds[0], pattern[2] == '1');
    gpiod_set_value_cansleep(data->leds[1], pattern[1] == '1');
    gpiod_set_value_cansleep(data->leds[2], pattern[0] == '1');

    data->state[0] = pattern[0];
    data->state[1] = pattern[1];
    data->state[2] = pattern[2];
    data->state[3] = '\n';
}

static ssize_t pi_led_write(
    struct file *file,
    const char __user *user_buffer,
    size_t count,
    loff_t *offset
)
{
    struct miscdevice *miscdev = file->private_data;
    struct pi_led_data *data = container_of(miscdev, struct pi_led_data, miscdev);

    char buffer[8];
    size_t len;

    if (count == 0)
        return 0;

    if (count >= sizeof(buffer))
        return -EINVAL;

    if (copy_from_user(buffer, user_buffer, count))
        return -EFAULT;

    buffer[count] = '\0';
    len = count;

    /* echo adds '\n', so remove it */
    if (len > 0 && buffer[len - 1] == '\n') {
        buffer[len - 1] = '\0';
        len--;
    }

    if (len == 1 && buffer[0] == '0') {
        pi_led_apply_pattern(data, "000");
        pr_info("pi-led: all LEDs off\n");
        return count;
    }

    if (len == 1 && buffer[0] == '1') {
        pi_led_apply_pattern(data, "001");
        pr_info("pi-led: LED1 on\n");
        return count;
    }

    if (
        len == 3 &&
        (buffer[0] == '0' || buffer[0] == '1') &&
        (buffer[1] == '0' || buffer[1] == '1') &&
        (buffer[2] == '0' || buffer[2] == '1')
    ) {
        pi_led_apply_pattern(data, buffer);
        pr_info("pi-led: pattern set to %s\n", buffer);
        return count;
    }

    pr_info("pi-led: invalid command: %s\n", buffer);
    return -EINVAL;
}

static ssize_t pi_led_read(
    struct file *file,
    char __user *user_buffer,
    size_t count,
    loff_t *offset
)
{
    struct miscdevice *miscdev = file->private_data;
    struct pi_led_data *data = container_of(miscdev, struct pi_led_data, miscdev);

    return simple_read_from_buffer(
        user_buffer,
        count,
        offset,
        data->state,
        sizeof(data->state)
    );
}

static const struct file_operations pi_led_fops = {
    .owner = THIS_MODULE,
    .write = pi_led_write,
    .read = pi_led_read,
};

static int pi_led_probe(struct platform_device *pdev)
{
    struct pi_led_data *data;
    int ret;
    int i;

    dev_info(&pdev->dev, "probing pi-led driver\n");

    data = devm_kzalloc(&pdev->dev, sizeof(*data), GFP_KERNEL);
    if (!data)
        return -ENOMEM;

    for (i = 0; i < LED_COUNT; i++) {
        data->leds[i] = devm_gpiod_get_index(
            &pdev->dev,
            "led",
            i,
            GPIOD_OUT_LOW
        );

        if (IS_ERR(data->leds[i])) {
            return dev_err_probe(
                &pdev->dev,
                PTR_ERR(data->leds[i]),
                "failed to get LED GPIO %d\n",
                i
            );
        }
    }

    data->state[0] = '0';
    data->state[1] = '0';
    data->state[2] = '0';
    data->state[3] = '\n';

    data->miscdev.minor = MISC_DYNAMIC_MINOR;
    data->miscdev.name = DEVICE_NAME;
    data->miscdev.fops = &pi_led_fops;
    data->miscdev.mode = 0666;

    ret = misc_register(&data->miscdev);
    if (ret) {
        dev_err(&pdev->dev, "failed to register /dev/%s\n", DEVICE_NAME);
        return ret;
    }

    platform_set_drvdata(pdev, data);

    dev_info(&pdev->dev, "created /dev/%s\n", DEVICE_NAME);

    return 0;
}

static void pi_led_remove(struct platform_device *pdev)
{
    struct pi_led_data *data = platform_get_drvdata(pdev);

    pi_led_apply_pattern(data, "000");
    misc_deregister(&data->miscdev);

    dev_info(&pdev->dev, "removed pi-led driver\n");
}

static const struct of_device_id pi_led_of_match[] = {
    { .compatible = "custom,pi-led" },
    { }
};

MODULE_DEVICE_TABLE(of, pi_led_of_match);

static struct platform_driver pi_led_driver = {
    .probe = pi_led_probe,
    .remove = pi_led_remove,
    .driver = {
        .name = "pi-led",
        .of_match_table = pi_led_of_match,
    },
};

module_platform_driver(pi_led_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Dakata99");
MODULE_DESCRIPTION("Raspberry Pi 3-LED character device driver using gpiod");