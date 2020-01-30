#include <rtl-sdr.h>

int main(void) {
    rtlsdr_dev_t *dev = (void*)0;
    rtlsdr_open(&dev, 0);
    rtlsdr_close(dev);
}
