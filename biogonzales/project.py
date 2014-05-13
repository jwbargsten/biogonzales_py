import os.path
import os
import logging
import yaml
import re
import json

class Project:
    def __init__(self, config_file = "gonz.conf.yml", merge_av_config = True ):
        self.config_file = config_file
        self.merge_av_config = merge_av_config
        self.project_dir = os.path.join("..", "..")
        self.analysis_version = self._init_av()
        self.log = self._init_log()
        self.log.info("invoked")
        self.config = None
        self._cache_conf()

    def _init_av(self):
        av = "."

        if 'ANALYSIS_VERSION' in os.environ:
            av = os.environ['ANALYSIS_VERSION']
        elif os.path.exists("av"):
            with open('av', 'r') as f:
                av = f.readline()
            av = av.rstrip("\n")

        if not os.path.exists(av):
            os.makedirs(av)
        return av

    def av(self):
        return self.analysis_version

    def _nfi(self, *path):
        return os.path.join(self.analysis_version, *path)

    def nfi(self, *path):
        p = self._nfi(*path)
        self.log.info(" ".join(["(nfi)", ">", p, "<"]))
        return p

    def conf(self, *keys):
        c = self.config
        has_keys = False
        for k in keys:
            c = c[k]
            has_keys = True
        msg = "(conf)"
        if has_keys:
            msg = " ".join([msg, "> ", keys, " <"])
        else:
            msg = " ".join([msg, "dump"])
            
        self.log.info("\n".join([msg, json.dumps(c, indent=2)]))
        return c

    def _cache_conf(self):
        if not self.config is None:
            return
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                conf = yaml.load(f)
            if not type(conf) is dict:
                raise TypeError("".join(["configuration file >> ", self.config_file, " << is not a hash/dictionary"]))
            self.log.info("".join(["reading >> ", self.config_file, " <<"]))

        av_config_file = ".".join([self.analysis_version, "conf", "yml"])
        if os.path.exists(av_config_file):
            with open(av_config_file, 'r') as f:
                av_conf = yaml.load(f)
            if not type(av_conf) is dict:
                raise TypeError("".join(["configuration file >> ", av_config_file, " << is not a hash/dictionary"]))
            conf.update(av_conf)
            self.log.info("".join(["reading >> ", av_config_file, " <<"]))

        self.config = self._visit_conf(conf)
        return

    def _init_log(self):
        logging.addLevelName(30, "WARN")
        log = logging.getLogger('biogonzales')
        hdlr = logging.FileHandler(self._nfi('gonz.log'))
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(module)s: %(message)s',
                datefmt="%Y-%m-%d %H:%M:%S")
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)
        log.setLevel(logging.INFO)
        return log

    def _visit_conf(self, it):
        if isinstance(it, str):
            if not re.match(r"^~[^/]*/", it) is None:
                it = os.path.expanduser(it)
            it = it.replace('__av__', self.analysis_version)
            m = re.match(r"__path_to\(([^)]+)\)__", it)
            if not m is None:
                it = re.sub('__path_to\([^)]+\)__', os.path.join(self.project_dir, m.group(1)), it)
            it = it.replace('__data__', os.path.join(self.project_dir, 'data'))
            return it
        elif (isinstance(it, list)):
            return type(it)(self._visit_conf(i) for i in it)
        elif (isinstance(it, dict)):
            for key in it.keys():
                it[key] = self._visit_conf(it[key])
            return it
        else:
            return it
