# coding=utf-8
'''
@ Summary: 
@ Update:  

@ file:    plugin_tflm_parser.py
@ version: 1.0.0

@ Author:  dkeji627@gmail.com
@ Date:    2021/9/29 21:50
'''
def platform_parameters(parser):
    """ imx6ull platform parameters """
    parser.add_argument("--ext_tools", type=str, default="", help="")
    parser.add_argument("--tflite", type=str, default="./platforms/plugin_tflm/TensorflowLiteMicro",
                        help="tensorflow lite micro dir")
    parser.add_argument("--rt_ai_example", type=str, default="./platforms/plugin_tflm/templates",
                        help="Model & platform informations registered to RT-AK Lib, eg:imx6ull, stm32, k210.")
    parser.add_argument("--tflm_out", type=str, default="",
                        help="TFLite output dir")
    parser.add_argument("--workspace", type=str, default="tflmai_ws",
                        help="indicates a working/temporary directory for the intermediate/temporary files")
    parser.add_argument("--val_data", type=str, default="",
                        help="indicates the custom test data set which must be used,"
                             "now is not supported")
    parser.add_argument("--compress", type=int, default=1,
                        help="indicates the expected global factor of compression which will be applied."
                             "1|4|8")
    parser.add_argument("--batches", type=int, default=10,
                        help="indicates how many random data sample is generated (default: 10)")
    parser.add_argument("--mode", type=str, default="001",
                        help="Describe analyze|validate|generate, 0 is False")
    parser.add_argument("--network", type=str, default="network",
                        help="The model name in '<tools>/Documents/<tflm> files'")
    parser.add_argument("--enable_rt_lib", type=str, default="RT_AI_USE_TFLM",
                        help="Enabel RT-AK Lib using tflite")
    parser.add_argument("--clear", action="store_true", help="remove tflm middleware")
    return parser
