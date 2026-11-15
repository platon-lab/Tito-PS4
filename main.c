// TITO PS4 — стадия 1: проверка геймпада.
// Треугольник — сменить цвет лайтбара. Крестик — вибрация. Options — выход.
#include <orbis/libkernel.h>
#include <orbis/Pad.h>
#include <orbis/UserService.h>
#include <orbis/Sysmodule.h>

static const uint8_t kColors[][3] = {
    {255, 0, 0}, {0, 255, 0}, {0, 0, 255},
    {255, 255, 0}, {255, 0, 255}, {0, 255, 255}
};
#define COLOR_COUNT (sizeof(kColors) / sizeof(kColors[0]))

int main(void) {
    sceSysmoduleLoadModule(ORBIS_SYSMODULE_PAD);
    sceUserServiceInitialize(NULL);

    int32_t userId = 0;
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

        if (pressed & ORBIS_PAD_BUTTON_TRIANGLE) {
            colorIndex = (colorIndex + 1) % COLOR_COUNT;
            OrbisPadLightBarParam light = {
                kColors[colorIndex][0],
                kColors[colorIndex][1],
                kColors[colorIndex][2]
            };
            scePadSetLightBar(pad, &light);
        }

        if (pressed & ORBIS_PAD_BUTTON_CROSS) {
            OrbisPadVibrationParam vib = { 255, 128 };
            scePadSetVibration(pad, &vib);
            sceKernelUsleep(300000);
            OrbisPadVibrationParam off = { 0, 0 };
            scePadSetVibration(pad, &off);
        }

        if (pressed & ORBIS_PAD_BUTTON_OPTIONS) {
            break;
        }

        sceKernelUsleep(16000);
    }

    scePadClose(pad);
    return 0;
}
