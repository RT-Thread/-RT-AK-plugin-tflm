/*
 * Copyright (c) 2006-2018, RT-Thread Development Team
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Change Logs:
 * Date           Author       Notes
 * 2021-09-29     derekduke    the first version
 */

#include <backend_tflm.h>
#include <rt_ai_log.h>
#ifdef RT_AI_USE_TFLM

#define tflm_load_model  person_detect_init
#define tflm_run_model   person_detect
#define tflm_get_model

extern uint32_t g_ai_done_flag;
static void kpu_done_callback(void *data)
{
    g_ai_done_flag = 1;
}

static int _tflm_init(rt_ai_t ai, rt_ai_buffer_t *buf)
{
    tflm_load_model(TFLITE(ai)->model);
    return 0;
}

static int _tflm_run(rt_ai_t ai, void (*callback)(void *arg), void *arg)
{
    tflm_run_model();
    return 0;
}

static int _tflm_get_ouput(rt_ai_t ai, rt_ai_uint32_t index)
{
    return 0;
}

static int _tflm_get_info(rt_ai_t ai, rt_ai_buffer_t *buf)
{
    return 0;
}

static int _tflm_config(rt_ai_t ai, int cmd, rt_ai_buffer_t *args)
{
    return 0;
}

int backend_tflm(void *tflm_s)
{
    RT_AI_T(tflm_s)->init = _tflm_init;
    RT_AI_T(tflm_s)->run = _tflm_run;
    RT_AI_T(tflm_s)->get_output = _tflm_get_ouput;
    RT_AI_T(tflm_s)->get_info = _tflm_get_info;
    RT_AI_T(tflm_s)->config = _tflm_config;
    RT_AI_T(tflm_s)->mem_flag = ALLOC_INPUT_BUFFER_FLAG;

    return 0;
}

#endif //RT_AI_USE_TFLM
