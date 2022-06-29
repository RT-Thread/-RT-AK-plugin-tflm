/*
 * Copyright (c) 2006-2018, RT-Thread Development Team
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Change Logs:
 * Date           Author       Notes
 * 2021-09-29     derekduke    the first version
 */

#ifndef __BACKEND_tflm_H__
#define __BACKEND_tflm_H__
#include <rtthread.h>
#include "rt_ai.h"
#ifdef RT_AI_USE_TFLM

struct tflm
{
    struct rt_ai parent;
    uint8_t                 *model;
};
typedef struct tflm *tflm_t;
#define TFLM(h)   ((tflm_t)(h))

int backend_tflm(void *tflm_s);
#endif //RT_AI_USE_TFLM
#endif

