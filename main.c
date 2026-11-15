// TITO PS4 — стадия 1: проверка геймпада.
// Треугольник — сменить цвет лайтбара. Крестик — вибрация. Options — выход.
#include <orbis/libkernel.h>
#include <orbis/Pad.h>
#include <orbis/UserService.h>
#include <stdint.h>

// Биты кнопок DualShock 4 (свои константы, чтобы не зависеть от имён макросов SDK)
#define BTN_OPTIONS  0x0008
#define BTN_TRIANGLE 0x1000
#define BTN_CROSS    0x4000

static const uint8_t kColors[6][3] = {
    {255, 0, 0}, {0, 255, 0}, {0, 0, 255},
    {255, 255, 0}, {255, 0, 255}, {0, 255, 255}
};

int main(void) {
    int32_t userId = 0;
    sceUserServiceInitialize(0);
    sceUserServiceGetInitialUser(&userId);

    scePadInit();
    int32_t pad = scePadOpen(userId, 0, 0, NULL);
    if (pad < 0) {
        return 1; // геймпад не найден
    }

    unsigned colorIndex = 0;
    uint32_t prevButtons = 0;

    for (;;) {
        OrbisPadData data;
        scePadReadState(pad, &data);
        uint32_t pressed = data.buttons & ~prevButtons;
        prevButtons = data.buttons;

        if (pressed & BTN_TRIANGLE) {
            colorIndex = (colorIndex + 1) % 6;
            OrbisPadColor color;
            color.r = kColors[colorIndex][0];
            color.g = kColors[colorIndex][1];
            color.b = kColors[colorIndex][2];
            scePadSetLightBar(pad, &color);
        }

        if (pressed & BTN_CROSS) {
            OrbisPadVibeParam vib;
            vib.largeMotor = 255;
            vib.smallMotor = 128;
            scePadSetVibration(pad, &vib);
            sceKernelUsleep(300000);
            vib.largeMotor = 0;
            vib.smallMotor = 0;
            scePadSetVibration(pad, &vib);
        }

        if (pressed & BTN_OPTIONS) {
            break;
        }

        sceKernelUsleep(16000);
    }

    scePadClose(pad);
    return 0;
}
