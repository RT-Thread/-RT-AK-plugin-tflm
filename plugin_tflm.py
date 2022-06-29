# coding=utf-8
'''
@ Summary: Platform: imx6ull
            1. check part
            2. prepare part
            3. convert model
            4. load lib
            5. load to project
@ Update:  

@ file:    plugin_imx6ull.py
@ version: 1.0.0

@ Author:  dkeji627@gmail.com
@ Date:    2021/09/29 20:55

@ Update:  
@ Date:

'''
import os
import sys
import re
import logging
import datetime
import shutil
from pathlib import Path


path = os.path.dirname(__file__)
sys.path.append(os.path.join(path, '../../'))

from platforms.plugin_tflm.config import *
from platforms.plugin_tflm import prepare_work
from platforms.plugin_tflm import generate_rt_ai_model_h
from platforms.plugin_tflm import gen_rt_ai_model_c


def readonly_handler(func, path):
    # Change the mode of file, to make it could be used of shutil.rmtree
    os.chmod(path, 128)
    func(path)


class Plugin(object):
    def __init__(self, opt):
        self.project = opt.project  # project path
        # self.model_path = os.path.abspath(opt.model)  # model path
        self.model_path = opt.model
        self.rt_ai_example = opt.rt_ai_example  # Documents
        self.platform = opt.platform
        self.c_model_name = opt.model_name.lower()  # c model name

        # config.py
        self.sup_models = sup_models
        self.sup_cpus = sup_cpus
        self.tflm_dirs = tflm_dirs  # tflite libraries
        self.sconscript_path = sconscript_path
        self.sup_modes = sup_modes  # support modes:{analyze, validate, generate}

        # imx6ull
        self.ext_tools = opt.ext_tools  
        self.tflite = opt.tflite  # tflite micro libraries
        self.network = opt.network  # default network name in sample files
        self.enable_rt_lib = opt.enable_rt_lib  # enable imx6ull in <pro>/rtconfig.h
        self.clear = opt.clear

        # setting aitools: tflm output path
        self.tflm_out = opt.tflm_out if opt.tflm_out else \
            datetime.date.today().strftime("%Y%m%d")

        # check the model
        self.is_valid_model(self.model_path, self.sup_models)

        # check the cpu
        self.cpu = self.is_valid_cpu(self.project, self.sup_cpus)


    def is_valid_model(self, model, sup_models):
        """ Determine whether the model supports"""
        # model suffix: ".h5"
        m_suf = Path(model).suffix

        # all supportted models suffix
        m_suf_lists = list()
        for value in sup_models.values():
            m_suf_lists += value

        logging.info("The model is '{}'".format(Path(model).name))
        if m_suf not in m_suf_lists:
            raise IOError("The '{}' is not surpported now...".format(model))


    def is_valid_cpu(self, project, sup_cpus, cpu=""):
        """ Determine whether the cpu supports"""
        project = Path(project)
        assert project.exists(), IOError("{} does not exist".format(project))

        # get cpu information
        sys.path.append(str(project))  # add rt_config.py path
        import rtconfig
        # CPU = 'imx6ull'
        real_cpu = rtconfig.CPU[7:].upper()  # M4 M7 M33
        real_cpu = "tflm" #手动强行赋值,暂时无平台差异
        print("real_cpu : " , real_cpu)
        # get chip information
        rt_config_path = project / "rtconfig.h"
        with open(rt_config_path, "r") as f:
            rt_config_text = f.read()
        #chip = re.findall(r"SOC_SERIES_STM32\w\d", rt_config_text)[0]
        #platform = chip[16:]  # H7 MP1 WL

        if real_cpu in sup_cpus:
            cpu = real_cpu
        #elif platform in sup_cpus:
        #    cpu = platform
        else:
            raise Exception("The cpu is not in supported now...")

        logging.info("The cpu is '{}'".format(cpu))
        return cpu


    def get_lib_path(self, stm_lib, cpu):
        """ load lib path """
        # select M7 folders
        for dir in os.listdir(stm_lib):
            if cpu in dir:
                lib_path = stm_lib / dir
                lib_path = list(filter(lambda path: "PIC" not in path.name, lib_path.iterdir()))[0]
                filename = "lib" + lib_path.name if stm_lib.name[:3] == "GCC" \
                    else lib_path.name
                return lib_path, filename


    def load_lib(self, tflm_out, tflite_path, cpu, middle=r"Middlewares/TF"):
        """ Loading tflite libs to <stm_out> from tflmai package

        Args:
            imx6ull_out: tflite output path, str
            tflite_path: tflite libraries
            path, str
            cpu: the project's cpu, str
            middle: r"Middlewares/TF/", str

        Returns:
            result: AI Lib files would be copied. list

        Raise:
            Failed copy Inc/Lib dir from <tflite_path> to <stm_out>
        """
        # list of aitools_out files
        result = list()
        target, source = Path(tflm_out), Path(tflite_path)
        # load tflite package path
        source_list = [source]
        target_list = [target / middle]
        
        # load Inc
        if target_list[0].exists():  # if the file have existed, delete it first.
            shutil.rmtree(target_list[0], onerror=readonly_handler)
        try:
            shutil.copytree(source_list[0], target_list[0])
        except Exception:
            raise Exception("Failed to load Inc???")
            
        logging.info("Loading tflm libs successfully...")


    def load_to_project(self, tflm_out, project, tflm_dirs):
        """ load TFLite / Middleware dir to project """
        # load TFLite & Middleware
        for path in tflm_dirs:
            source, target = Path(tflm_out) / path, Path(project) / path
            if target.exists():
                shutil.rmtree(target, onerror=readonly_handler)
            try:
                shutil.copytree(source, target)
            except Exception:
                raise Exception("Failed to load {}???".format(path))
            logging.info("{} loading to project successfully...".format(source.name))

    def c_model_convert(self, tflm_out , model_path):
        c_model_name = model_path[9:-7]
        tflite_model = Path(tflm_out) / "TFLite/App"
        assert tflite_model.exists(), "No TFLite/App exists, pls check the path!!!"

        # convert model to c_model
        model_data_c_path = str(tflite_model)+"/"+c_model_name+"_data.c"
        model_data_h_path = str(tflite_model)+"/"+c_model_name+"_data.h"

        print("c_model_name: " + c_model_name)
        #if model_data_c.exists():  model_data_c.unlink()
        print("model_data_c path:" , model_data_c_path)

        os.system("xxd -i "+ "./Models/"+c_model_name +".tflite"+" > " +model_data_c_path)
        print("xxd convert over")
        with open(model_data_c_path , 'r+') as f:
            content = f.read()
            f.seek(0,0)
            include_path = "#include <TFLite/APP/"+c_model_name+"_data.h>\n\n"
            f.write(include_path+'const '+content)

        with open(model_data_h_path , 'w+') as f:
            content = f.read()
            f.seek(0,0)
            c_model_data_define = "extern const unsigned char" + " __Models_"+c_model_name+"_tflite[];\n"
            f.write(c_model_data_define)

    def run_plugin(self,):
        """start tflite micro: running """
        logging.info("start to run_plugin...")
        # 1. prepare part
        # 1.1 imx6ull ext_tools env settings

        # 1.2 create two dirs and SConscripts
        prepare_work.pre_sconscript(self.tflm_out, self.sconscript_path, self.tflm_dirs)

        # 2. convert model
        _ = self.c_model_convert(self.tflm_out, self.model_path)
  
        # 3.1 generate rt_ai_<model_name>_model.h
        _ = generate_rt_ai_model_h.rt_ai_model_gen(self.tflm_out, self.project,
                                                   self.c_model_name, self.rt_ai_example) 
       
        # 3.2 load rt_ai_<model_name>_model.c
        _ = gen_rt_ai_model_c.load_rt_ai_example(self.project, self.rt_ai_example, self.platform,
                                                 self.network, self.c_model_name)

        # 4. load lib from <tflite> to <stm_out>
        # copy lib files from tflm to current dir
        self.load_lib(self.tflm_out, self.tflite, self.cpu)

        # 5. load <stm_out> to project
        self.load_to_project(self.tflm_out, self.project, self.tflm_dirs)

        # 6. remove imx6ull output dirs or not
        if os.path.exists(self.tflm_out) and self.clear:
            shutil.rmtree(self.tflm_out, onerror=readonly_handler)

if __name__ == "__main__":
    os.chdir("../..")
    logging.getLogger().setLevel(logging.INFO)

    class Opt():
        def __init__(self):
            self.tflite = "./platforms/tflm/TensorflowLiteMicro"

    opt = Opt()
    tflm = Plugin(opt)
    tflm.run_plugin()
