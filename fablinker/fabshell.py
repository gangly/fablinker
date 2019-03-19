#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import cmd
import getpass
import subprocess
import functools
import fabric.api as fab
from fabric.colors import *

from fablinker.compat import config_parser
from fablinker.constant import CMD_PROMPT
from fablinker.utils import ColorPrint, parse_config


def fab_execute(func):
    @functools.wraps(func)
    def wrapper(*args):
        return fab.execute(func, *args)
    return wrapper


class FabShell(cmd.Cmd):
    """
    A simple fabric shell
    """
    def __init__(self, conf_file):
        cmd.Cmd.__init__(self)
        self.conf_file = conf_file
        self.base_conf, self.host_groups, self.current_group = parse_config(conf_file)

        for key in self.base_conf:
            fab.env[key] = self.base_conf[key]

        fab.env.hosts = self.host_groups[self.current_group]
        if not fab.env.user:
            fab.env.user = getpass.getuser()
        fab.env.warn_only = True
        fab.env.colorize_errors = True
        fab.env.skip_bad_hosts = True

        self.cwd_list = ['home', fab.env.user]
        self.conf_changed = False
        self.all_hosts = set([])
        self.disconnect_hosts = set([])
        self.set_cmd_prompt(self.current_group)

    def do_save(self, *args):
        self.save_config(self.conf_file)

    def save_config(self, conf_file):
        """
        save configure file
        """
        try:
            cf = config_parser()
            cf.optionxform = str
            cf.read(conf_file)
            cf.set('baseconf', 'user', fab.env.user)
            cf.set('baseconf', 'password', fab.env.password)
            cf.set('baseconf', 'parallel', fab.env.parallel)
            for group, hosts in self.host_groups.items():
                hosts_str = '[' + ','.join(hosts) + ']'
                cf.set('host_groups', group, hosts_str)
            cf.write(open(conf_file, 'w'))
            return True
        except Exception as e:
            ColorPrint.red(e.message)



    def set_fabp(self, *args):
        args_list = args[0]
        fab_kw = args[1]
        args_list.remove('-fabp')
        fab_kw['parallel'] = True

    def set_fabs(self, *args):
        args_list = args[0]
        fab_kw = args[1]
        args_list.remove('-fabs')
        fab_kw['parallel'] = False

    def set_fabh(self, *args):
        args_list = args[0]
        fab_kw = args[1]

        idx = args_list.index('-fabh')
        hosts_str = args_list.pop(idx+1)
        fab_hosts = hosts_str.split(',')

        args_list.remove('-fabh')
        fab_kw['hosts'] = fab_hosts

    @fab_execute
    def fab_run(self, args):
        try:
            return fab.run(args)
        except Exception as e:
            raise e

    def fab_task_cd(self, args):
        ret = self.fab_run(args)
        for host in ret:
            if not ret[host].succeeded:
                return True
        tmp_cwd = args.split()[-1]
        if tmp_cwd.startswith('~'):
            self.cwd_list = ['home', fab.env.user]
            self.cwd_list += tmp_cwd[1:].strip('/').split('/')
        elif tmp_cwd.startswith('..'):
            self.cwd_list.pop()
            self.cwd_list += tmp_cwd[2:].strip('/').split('/')
        elif tmp_cwd.startswith('.'):
            self.cwd_list += tmp_cwd[1:].strip('/').split('/')
        elif tmp_cwd.startswith('/'):
            self.cwd_list = tmp_cwd.strip('/').split('/')
        else:
            self.cwd_list += tmp_cwd.strip('/').split('/')

        fab.env.cwd = '/' + '/'.join(self.cwd_list)
        print (fab.env.cwd)
        print ()
        return True

    def fab_task_checkhosts(self, args):
        for group, hosts in self.host_groups.items():
            self.all_hosts |= set(hosts)
        for host in self.all_hosts:
            try:
                with fab.settings(hosts=[host]):
                    with fab.hide('running', 'stdout', 'stderr'):
                        ret = self.fab_run('date')
                        if ret[host].succeeded:
                            print(host, 'connected ok.')
                        else:
                            ColorPrint.red('%s connected failed!' % host)
                            self.disconnect_hosts.add(host)
            except Exception as e:
                ColorPrint.red('%s connected failed!' % host)
                self.disconnect_hosts.add(host)
        return True

    def fab_task_bt(self, args):
        cmd_file = args.strip()[2:].strip()
        print(cmd_file)
        try:
            with open(cmd_file, 'r') as f:
                for line in f.readlines():
                    self.fab_run(line.strip())
                return True
        except Exception as e:
            ColorPrint.red(e)
        return True

    def do_fab(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : execute shell command on remote hosts
        usage: fab [-fabp/-fabs] [-fabh host1,host2,...] cmd [&]
               & : running task on deamon
               -fabp : parallel executing command on all hosts
               -fabs : serial executing command on all hosts
               -fabh host1,host2,...: execute command on just host1,host2...
        eg   : fab -fabh [host1,host2] php test.php &
               fab -fabp mkdir /home/work/hello
        """
        try:
            args_list = args.split()
            fab_kw = {}
            for arg in args.split():
                if arg.startswith('-fab'):
                    self.callback('set_', arg[1:], args_list, fab_kw)
            
            args = ' '.join(args_list)
            # check whether the task is running on deamon
            if args[-1] == '&':
                args = 'nohup ' + args + ' disown;sleep 1'
            with fab.settings(**fab_kw):
                if self.callback('fab_task_', args_list[0], args):
                    return
                self.fab_run(args)

        except Exception as e:
            ColorPrint.red('cmd error, %s' % e)
            ColorPrint.blue(self.do_fab.__doc__)

    def do_setparallel(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : set execute parallel status (default False)
        usage: setparallel [True/true/False/false]
        """
        if args in ('True', 'true', 'False', 'false'):
            fab.env.parallel = args.capitalize()
            print('set execute parallel %s successfully!' % args)

    @fab_execute
    def fab_put(self, local_path, remote_path):
        fab.put(local_path, remote_path)

    def do_put(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : put local files to remote servers
        usage: put local_path remote_path
        eg   : put ./hosts.ini ~/test/
        """
        args_list = args.split()
        if len(args_list) < 2:
            ColorPrint.blue(self.do_put.__doc__)
        else:
            self.fab_put(args_list[0], args_list[1])

    @fab_execute
    def fab_get(self, remote_path, local_path):
        fab.get(remote_path, local_path)

    def do_get(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : get files from remote servers
        usage: get [-n] local_path remote_path
               -n : save remote file to file0, file1...
               default : filehostname0, filehostname1...
        eg   : get -n /home/work/eg ~/get/test.txt
               /home/work/eg/test.txt0
               /home/work/eg/test.txt1
               ...
               get /home/work/eg ~/get/test.txt
               /home/work/eg/test.txtnj02-vs-ting-ensl-34.nj02
               /home/work/eg/test.txtcq02-lightapp-stat09.cq02
        """
        try:      
            args_list = args.split()
            if '-n' in args_list:
                args_list.remove('-n')
           
            local_path = args_list[0]
            remote_path = args_list[1]
            if len(fab.env.hosts) > 1:
                prefix = remote_path.split('/')[-1]
                for i, host in enumerate(fab.env.hosts):
                    with fab.settings(hosts=[host]):
                        tmp_local_path = local_path+'/'+prefix+host
                        self.fab_get(remote_path, tmp_local_path)
            else:
                self.fab_get(remote_path, local_path)
        except IndexError:
            ColorPrint.red('not enough parameters')
        except Exception as e:
            ColorPrint.red('bad command, %s' % e)
            ColorPrint.blue(self.do_get.__doc__)

    def do_shell(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : run a shell commad on local server
        usage: !shellcmd
        eg   : !ls
        """
        sub_cmd = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
        print(sub_cmd.communicate()[0])

    def callback(self, prefix, name, *args):
        method = getattr(self, prefix+name, None)
        if callable(method):
            return method(*args)
            # method(*args)

    def ls_g(self):
        for group in self.host_groups.keys():
            print(group)
        print()

    def ls_a(self):
        for group, hosts in self.host_groups.items():
            print(blue(group+':'))
            for host in hosts:
                print(host)
            print()
        print()

    def ls_env(self):
        print('user :', fab.env.user)
        print('cwd  :', fab.env.cwd)
        print('parallel :', fab.env.parallel)
        print()

    def do_ls(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : list remote hosts
        usage: list [-a/-g/-env]
               list : list current hosts
               -g : list all group
               -a : list all hosts
               -env : list environment variables
        """
        args = args.strip()
        if not args.strip():
            for i, host in enumerate(fab.env.hosts):
                print('%d | %s' % (i, host))
        else:
            name = args[1:]
            self.callback('ls_', name)


    def do_addgrp(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : add a new remote host group,
        usage: addgrp group_name host1 host2 ... hostn
        """
        args_list = args.split()
        try:
            group_name = args_list[0]
            hosts = args_list[1:]
        except IndexError:
            ColorPrint.blue(self.do_addgrp.__doc__)
        else:
            self.host_groups[group_name] = hosts
            self.conf_changed = True

    def do_rmgrp(self, args):
        '''
        -*-*-*-*-*-*-*-*-
        desc : remove a remote host group,
        usage: rmgrp group_name
        '''
        group = args.strip()
        if group:
            try:
                self.host_groups.pop(group)
            except KeyError:
                ColorPrint.red('not find %s host group' % group)
                print()
            else:
                self.conf_changed = True

    def set_cmd_prompt(self, meg):
        self.prompt = yellow("%s%s " % (meg, CMD_PROMPT))

    def do_at(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : switch to a group or a host
        usage: at group_name/host_name
        """
        args = args.strip()
        for group, hosts in self.host_groups.items():
            if args == group:
                fab.env.hosts = hosts
                self.set_cmd_prompt(args)
                break
            if args in hosts:
                fab.env.hosts = [args, ]
                self.set_cmd_prompt(args)
                break
        
        ColorPrint.red('Error : can not find any group or host')

    def do_pwd(self, args):
        """
        -*-*-*-*-*-*-*-*-
        desc : show the current directory path
        usage: pwd
        """
        print(fab.env.cwd if fab.env.cwd else '/home/work')
        print()

    def do_exit(self, args):
        """
        desc : terminatesthe application
        usage: exit
        """
        # disconnect_all()
        if self.conf_changed:
            self.save_config(self.conf_file)
        return True
