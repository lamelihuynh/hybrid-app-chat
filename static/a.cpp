// wrap_bypass.c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

long get_integer_less_than(int limit) {
    long v;
    if (scanf("%ld", &v) != 1) {
        puts("Input error");
        exit(1);
    }
    // LỖ HỔNG: chỉ kiểm tra giới hạn phía trên
    if (v >= limit) {
        puts("Too large!");
        exit(1);
    }
    return v;
}

int main(void) {
    puts("Question A: Provide a number less than 10:");
    // người viết tưởng rằng chỉ cần kiểm tra < 10 rồi cast xuống uint16_t là an toàn
    uint16_t a = (uint16_t) get_integer_less_than(10);
    if (a == 11) {
        puts("Answer A correct!");
    } else {
        printf("Answer A as uint16 = %u\n", (unsigned int)a);
    }

    puts("Question B: Provide a number less than 69:");
    uint16_t b = (uint16_t) get_integer_less_than(69);
    if (b == 96) {
        puts("Answer B correct!");
    } else {
        printf("Answer B as uint16 = %u\n", (unsigned int)b);
    }

    return 0;
}
