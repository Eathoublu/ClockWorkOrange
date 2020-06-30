# coding:utf8
import threading
import time
import matplotlib.pyplot as plt


class BaseComponent(object):
    def __init__(self, _respoense_time):
        return

    def input(self):
        return

    def output(self):
        return

    def statusupdate(self):
        return

    def __set_input(self):
        return


class BaseGate(BaseComponent):
    def __init__(self, _respoense_time):
        return

    def input(self):
        return

    def output(self):
        return

    def statusupdate(self):
        return

    def __set_input(self):
        return


class LOGIC:
    HIGH = True
    LOW = False

class PIN:
    @staticmethod
    def IN(num):
        return 'IN{}'.format(num)
    @staticmethod
    def OUT(num):
        return 'OUT{}'.format(num)
    @staticmethod
    def COMPONENT_OUTPIN(component, num):
        return '{}_{}'.format(component, num)



class NAND(BaseGate):
    def __init__(self, _input_num=2, _response_time=0.000002):
        self.is_breakover = False
        self.input_dict = {}
        for idx in range(_input_num):
            self.input_dict[idx] = False
        self.response_time = _response_time

    def input(self, input_table={'port': [], 'set': []}):
        if len(input_table['port']) != len(input_table['set']):
            raise Exception('PortError', 'mismatching port length!')
        self.__set_input(input_table, )
        return

    def __set_input(self, inputtable):
        for portidx in range(len(inputtable['port'])):
            self.input_dict[inputtable['port'][portidx]] = inputtable['set'][portidx]
        self.statusupdate()
        return

    def statusupdate(self):
        for k in self.input_dict:
            if not self.input_dict[k]:
                self.is_breakover = True
                return
        self.is_breakover = False
        return

    def output(self):
        return self.is_breakover


class InputPort(BaseComponent):
    def __init__(self, _respoense_time):
        self.status = False
        self.response_time = _respoense_time
        return

    def __set_input(self, _in):
        time.sleep(self.response_time)
        self.status = False
        return

    def input(self, _in):
        t1 = threading.Thread(target=self.__set_input, args=(_in,))
        t1.start()
        return

    def output(self):
        return self.status


class Component(BaseComponent):
    def __init__(self, _input_num, _output_num, _response_time=0.000002, _response_time_onwire=0.0005,
                 _max_update_time=50,
                 _judge_steady_time=3,
                 _name=None):

        self.__responsetime = _response_time
        self.__responsetime_onwire = _response_time_onwire
        self.graph = {}
        self.component = {}
        self.output_num = _output_num
        self.name = _name
        self.__currentstate = {}
        self.__outputstatus = {}
        self.__outputstatus_history = []
        self.__max_update_time = _max_update_time
        self.__updatetime = 0
        self.__port_num = 1
        self.__judge_steady_times = _judge_steady_time
        for idx in range(_input_num):
            self.graph['IN{}'.format(idx)] = []

        for idx in range(_output_num):
            self.graph['OUT{}'.format(idx)] = None
            self.__outputstatus['OUT{}'.format(idx)] = False


    def set_name(self, name):
        if name is not None:
            self.name = name
        return

    def add(self, component, network_port, exist_component=None, component_name=None):

        example_graph_v1 = {
            'IN1': [{'_ComponentName_': 'G1', '_ComponentPortNum_': [0, 1], '_Component_': component}],
            'G1': [{'_ComponentName_': 'OUT', '_ComponentPortNum_': [0, ], '_Component_': None},
                   {'_ComponentName_': 'OUT1', '_ComponentPortNum_': [0, ], '_Component_': None}]
        }
        example_graph_v2 = {
            'IN1': [{'_ComponentName_': 'G1', '_ComponentPortNum_': [0, 1]}],
            'G1': [{'_ComponentName_': 'OUT', '_ComponentPortNum_': [0, ], '_Component_': None}]
        }
        network_port_example_v2 = {'IN0': [0, 1]}
        if isinstance(component, str):
            if 'OUT' not in component:
                raise Exception("ComponentTypeError", 'Component type must be BaseComponent or "OUT". ')
            if 'OUT' in component:
                for k in network_port:
                    if k not in self.graph:
                        raise Exception('AddOutPinError', "Cannot find correspond component.")
                    self.graph[k].append({'_ComponentName_': component, '_ComponentPortNum_': None})
                return

        if not (component_name or exist_component):
            raise Exception("AddComponentError", "You must specify a name for the component.")

        if not exist_component:
            if component_name not in self.graph:
                self.graph[component_name] = []
            for k in network_port:
                if not k in self.graph:
                    self.graph[k] = []
                    self.graph[k].append({'_ComponentName_': component_name, '_ComponentPortNum_': network_port[k]})
                    self.component[component_name] = component
                elif k in self.graph:
                    self.graph[k].append({'_ComponentName_': component_name, '_ComponentPortNum_': network_port[k]})
                    self.component[component_name] = component
            return

    def input(self, input_table={'port': [], 'set': []}):

        self.__set_input(input_table, )

    def __set_input(self, inputtable):
        inputtable_example = {'IN0': True, 'In1': False}
        time.sleep(self.__responsetime)
        trigger_list = set()

        for k in range(len(inputtable['port'])):
            for c in self.graph[inputtable['port'][k]]:
                self.component[c['_ComponentName_']].input({'port': c['_ComponentPortNum_'],
                                                            'set': [inputtable['set'][k] for _ in
                                                                    range(len(c['_ComponentPortNum_']))]})
                trigger_list.add(c['_ComponentName_'])
        self.__updatetime = 1

        self.__statusupdate(trigger_list, )

    def __statusupdate(self, _trig):
        if self.__updatetime >= self.__max_update_time:
            print('REACH MAX')
            self.__clean_cache()
            return
        _trig_2 = set()
        time.sleep(self.__responsetime_onwire)

        for c in list(_trig):
            status = self.component[c].output()

            for p in self.graph[c]:
                if not 'OUT' in p['_ComponentName_']:

                    self.component[p['_ComponentName_']].input(
                        {'port': p['_ComponentPortNum_'], 'set': [status for _ in range(len(p['_ComponentPortNum_']))]})
                    _trig_2.add(p['_ComponentName_'])
                else:
                    self.__outputstatus[p['_ComponentName_']] = status


        output_status = [self.__outputstatus[k] for k in self.__outputstatus]
        self.__outputstatus_history.append(output_status)
        if len(self.__outputstatus_history) > self.__judge_steady_times + 2:

            for idx in range(1, self.__judge_steady_times, 1):
                if idx == self.__judge_steady_times - 1:

                    self.__clean_cache()
                    return
                if self.__outputstatus_history[-idx] == self.__outputstatus_history[-(idx + 1)]:
                    continue
                else:
                    break

        if _trig_2:
            self.__updatetime += 1
            self.__statusupdate(_trig_2)
        else:
            self.__clean_cache()
            return
        self.__clean_cache()
        return

    def __clean_cache(self):
        self.__updatetime = 0
        self.__outputstatus_history = []

    def summary(self):
        return

    def __str__(self):
        return

    def output(self):
        return self.__outputstatus

class Circuit(Component):
    def __init__(self, _input_num, _output_num,
                 _response_time=0.000002,
                 _response_time_onwire=0.0005,
                 _max_update_time=50,
                 _judge_steady_time=3,
                 _name=None):
        super(Circuit, self).__init__(_input_num, _output_num,
                                      _response_time=_response_time,
                                      _response_time_onwire=_response_time_onwire,
                                      _max_update_time=_max_update_time,
                                      _judge_steady_time=_judge_steady_time,
                                      _name=_name)
        self.__component_port = {}

        self.__responsetime = _response_time
        self.__responsetime_onwire = _response_time_onwire
        self.__currentstate = {}
        self.__outputstatus = {}
        self.__outputstatus_history = []
        self.__max_update_time = _max_update_time
        self.__updatetime = 0
        self.__port_num = 1
        self.__judge_steady_times = _judge_steady_time

        for idx in range(_input_num):
            self.graph['IN{}'.format(idx)] = []
        for idx in range(_output_num):
            self.graph['OUT{}'.format(idx)] = None
            self.__outputstatus['OUT{}'.format(idx)] = False

    def add(self, component, network_port, exist_component=None, component_name=None):
        # port_conn=[]
        example_graph_v1 = {
            'IN1': [{'_ComponentName_': 'G1', '_ComponentPortNum_': [0, 1], '_Component_': component}],
            'G1': [{'_ComponentName_': 'OUT', '_ComponentPortNum_': [0, ], '_Component_': None},
                   {'_ComponentName_': 'OUT1', '_ComponentPortNum_': [0, ], '_Component_': None}]
        }
        example_graph_v2 = {
            'IN1': [{'_ComponentName_': 'G1', '_ComponentPortNum_': [0, 1]}],
            'G1': [{'_ComponentName_': 'OUT', '_ComponentPortNum_': [0, ], '_Component_': None}]
        }
        network_port_example_v2 = {'IN0': [0, 1]}
        if isinstance(component, str):
            if 'OUT' not in component:
                raise Exception("ComponentTypeError", 'Component type must be BaseComponent or "OUT". ')
            if 'OUT' in component:
                for k in network_port:
                    if k not in self.graph:
                        raise Exception('AddOutPinError', "Cannot find correspond component.")
                    self.graph[k].append({'_ComponentName_': component, '_ComponentPortNum_': None})
                return

        if isinstance(component, BaseGate):

            if not (component_name or exist_component):
                raise Exception("AddComponentError", "You must specify a name for the component.")

            if not exist_component:
                if component_name not in self.graph:
                    self.graph[component_name] = []
                    self.__component_port[component_name] = [component_name, ]
                for k in network_port:
                    if not k in self.graph:
                        self.graph[k] = []
                        self.graph[k].append({'_ComponentName_': component_name, '_ComponentPortNum_': network_port[k]})
                        self.component[component_name] = component
                    elif k in self.graph:
                        self.graph[k].append({'_ComponentName_': component_name, '_ComponentPortNum_': network_port[k]})
                        self.component[component_name] = component
                return
            else:
                pass

        if isinstance(component, Component):

            if not (component_name or exist_component):
                raise Exception("AddComponentError", "You must specify a name for the component.")

            if not exist_component:
                self.__component_port[component_name] = []
                for k in range(component.output_num):
                    if '{}_{}'.format(component_name, k) not in self.graph:
                        self.graph['{}_{}'.format(component_name, k)] = []
                    self.__component_port[component_name].append('{}_{}'.format(component_name, k))

                for k in network_port:
                    if not k in self.graph:
                        self.graph[k] = []
                        self.graph[k].append({'_ComponentName_': component_name, '_ComponentPortNum_': network_port[k]})
                        self.component[component_name] = component
                    elif k in self.graph:
                        self.graph[k].append({'_ComponentName_': component_name, '_ComponentPortNum_': network_port[k]})
                        self.component[component_name] = component
                return

            else:
                pass

            pass

        raise Exception('AddComponentError', 'Component type not match. Component must be BaseGate, Component or "OUT". ')


    def __statusupdate(self, _trig):
        if self.__updatetime >= self.__max_update_time:
            print('REACH MAX')
            self.__clean_cache()
            return
        _trig_2 = set()
        time.sleep(self.__responsetime_onwire)
        for c in list(_trig):
            status = self.component[c].output()
            if isinstance(status, bool):

                for p in self.graph[c]:
                    if not 'OUT' in p['_ComponentName_']:

                        if isinstance(self.component[p['_ComponentName_']], Component):
                            self.component[p['_ComponentName_']].input(
                                {'port': ['IN{}'.format(_p) for _p in p['_ComponentPortNum_']],
                                 'set': [status for _ in
                                         range(len(p['_ComponentPortNum_']))]})
                        elif isinstance(self.component[p['_ComponentName_']], BaseGate):

                            self.component[p['_ComponentName_']].input(
                                {'port': p['_ComponentPortNum_'],
                                 'set': [status for _ in range(len(p['_ComponentPortNum_']))]})

                        _trig_2.add(p['_ComponentName_'])
                    else:
                        self.__outputstatus[p['_ComponentName_']] = status


            if isinstance(status, dict):

                _status = {}
                for k in status:
                    _status[k.replace('OUT', c+'_')] = status[k]

                for k in _status:
                    for p in self.graph[k]:
                        if not 'OUT' in p['_ComponentName_']:

                            if isinstance(self.component[p['_ComponentName_']], Component):
                                self.component[p['_ComponentName_']].input(
                                    {'port': ['IN{}'.format(_p) for _p in p['_ComponentPortNum_']],
                                     'set': [_status[k] for _ in
                                             range(len(p['_ComponentPortNum_']))]})
                            elif isinstance(self.component[p['_ComponentName_']], BaseGate):
                                # print('HERE 3')
                                self.component[p['_ComponentName_']].input(
                                    {'port': p['_ComponentPortNum_'],
                                     'set': [_status[k] for _ in range(len(p['_ComponentPortNum_']))]})

                            _trig_2.add(p['_ComponentName_'])
                        else:
                            self.__outputstatus[p['_ComponentName_']] = _status[k]

        output_status = [self.__outputstatus[k] for k in self.__outputstatus]
        self.__outputstatus_history.append(output_status)
        if len(self.__outputstatus_history) > self.__judge_steady_times + 2:

            for idx in range(1, self.__judge_steady_times, 1):
                if idx == self.__judge_steady_times - 1:

                    self.__clean_cache()
                    return
                if self.__outputstatus_history[-idx] == self.__outputstatus_history[-(idx + 1)]:
                    continue
                else:
                    break

        if _trig_2:
            self.__updatetime += 1
            self.__statusupdate(_trig_2)
        else:
            self.__clean_cache()
            return
        self.__clean_cache()
        return

    def __set_input(self, inputtable):

        inputtable_example = {'IN0': True, 'IN1': False}
        time.sleep(self.__responsetime)
        trigger_list = set()

        for k in range(len(inputtable['port'])):
            for c in self.graph[inputtable['port'][k]]:
                if isinstance(self.component[c['_ComponentName_']], Component):
                    self.component[c['_ComponentName_']].input({'port': ['IN{}'.format(p) for p in c['_ComponentPortNum_']],
                                                                'set': [inputtable['set'][k] for _ in
                                                                        range(len(c['_ComponentPortNum_']))]})
                if isinstance(self.component[c['_ComponentName_']], BaseGate):
                    self.component[c['_ComponentName_']].input({'port': c['_ComponentPortNum_'],
                                                                'set': [inputtable['set'][k] for _ in
                                                                        range(len(c['_ComponentPortNum_']))]})
                trigger_list.add(c['_ComponentName_'])
        self.__updatetime = 1

        self.__statusupdate(trigger_list, )


    def input(self, input_table={'port': [], 'set': []}):

        self.__set_input(input_table, )

    def __clean_cache(self):
        self.__updatetime = 0
        self.__outputstatus_history = []

    def output(self):
        return self.__outputstatus




class Tester(object):
    def __init__(self, circuit, watchlist, clock_frepency=3, clock_pin=None, duty_cycle=0.5, trigger=0, max_terms=500, initial_impulse=None, use_num_for_plot=True, verbose=True):
        self.circuit = circuit
        self.__clock_fequency = clock_frepency
        self.__cp = clock_pin
        self.__duty_cycle = duty_cycle
        self.__trigger = trigger
        self.__slot = 1./self.__clock_fequency*self.__duty_cycle
        self.__one_term = 1./self.__clock_fequency
        self.__max_terms = max_terms
        self.__inital_impulse = initial_impulse
        self.__start_time = time.time()
        self.__outputstatus = {}
        self.__use_num_for_plot = use_num_for_plot
        self.__impulse_num = 0
        self.__watchlist = watchlist
        self.figure_size = (20, 10)
        self.verbose = verbose

        if self.__inital_impulse and self.__cp:
            self.clockwork(_max=self.__inital_impulse)

    def clockwork(self, _max=None):
        if _max:
            term = 1
            while term < _max:
                if self.__trigger == 0:
                    self.__set_clock(LOGIC.HIGH)
                    self.__set_clock(LOGIC.LOW)
                else:
                    self.__set_clock(LOGIC.LOW)
                    self.__set_clock(LOGIC.HIGH)
                term += 1

                self.__sample()
            return
        term = 1
        while term < self.__max_terms:
            if self.__trigger == 0:
                self.__set_clock(LOGIC.HIGH)
                self.__set_clock(LOGIC.LOW)
            else:
                self.__set_clock(LOGIC.LOW)
                self.__set_clock(LOGIC.HIGH)
            term += 1

            self.__sample()
        return


    def __set_clock(self, logic):
        self.circuit.input({'port': [self.__cp], 'set': [logic, ]})
        print('LOGIC {}'.format(logic))
        self.__sample(clockstatus=logic)
        time.sleep(self.__slot)




    def input(self, vector):

        for bitidx in range(len(vector['IN1'])):

            self.circuit.input({'port': [self.__cp], 'set': [LOGIC.HIGH]})
            self.__sample(clockstatus=LOGIC.HIGH)
            time.sleep(self.__slot)

            self.circuit.input({'port': [self.__cp], 'set': [LOGIC.LOW]})
            self.circuit.input({'port': [k for k in vector], 'set': [vector[k][bitidx] for k in vector]})

            _inputvector = {}
            for k in vector:
                _inputvector[k] = vector[k][bitidx]
            self.__sample(clockstatus=LOGIC.LOW, invector=_inputvector)
            if self.verbose:
                print('COMPONENT OUTPUT : {}'.format(self.circuit.output()))
            time.sleep(self.__slot)


    def __sample(self, type=['OUTPUT', 'CP', 'INPUT'], clockstatus=None, invector = None):
        watchlist = self.__watchlist
        if 'OUTPUT' in type:
            status = self.circuit.output()
            self.__impulse_num += 1
            for OUTPIN in watchlist:
                if OUTPIN not in self.__outputstatus:
                    self.__outputstatus[OUTPIN] = {'x':[], 'y': []}
                if OUTPIN in status:
                    if status[OUTPIN]:
                        if self.__use_num_for_plot:
                            _current = self.__impulse_num
                        else:
                            _current = time.time()-self.__start_time
                        self.__outputstatus[OUTPIN]['x'].append(_current)
                        if len(self.__outputstatus[OUTPIN]['y']) >= 1:
                            if self.__outputstatus[OUTPIN]['y'][-1] == 1:
                                self.__outputstatus[OUTPIN]['y'].append(1)
                            else:
                                self.__outputstatus[OUTPIN]['y'].append(0)
                                self.__outputstatus[OUTPIN]['x'].append(_current)
                                self.__outputstatus[OUTPIN]['y'].append(1)
                        else:
                            self.__outputstatus[OUTPIN]['y'].append(1)
                    else:
                        if self.__use_num_for_plot:
                            _current = self.__impulse_num
                        else:
                            _current = time.time()-self.__start_time
                        self.__outputstatus[OUTPIN]['x'].append(_current)

                        if len(self.__outputstatus[OUTPIN]['y']) >= 1:
                            if self.__outputstatus[OUTPIN]['y'][-1] == 0:
                                self.__outputstatus[OUTPIN]['y'].append(0)
                            else:
                                self.__outputstatus[OUTPIN]['y'].append(1)
                                self.__outputstatus[OUTPIN]['x'].append(_current)
                                self.__outputstatus[OUTPIN]['y'].append(0)
                        else:
                            self.__outputstatus[OUTPIN]['y'].append(0)
        if 'CP' in type and clockstatus is not None:

            if 'CP' not in self.__outputstatus:
                self.__outputstatus['CP'] = {'x': [], 'y': []}

            OUTPIN = 'CP'

            if clockstatus:
                if self.__use_num_for_plot:
                    _current = self.__impulse_num
                else:
                    _current = time.time() - self.__start_time
                self.__outputstatus[OUTPIN]['x'].append(_current)
                if len(self.__outputstatus[OUTPIN]['y']) >= 1:
                    if self.__outputstatus[OUTPIN]['y'][-1] == 1:
                        self.__outputstatus[OUTPIN]['y'].append(1)
                    else:
                        self.__outputstatus[OUTPIN]['y'].append(0)
                        self.__outputstatus[OUTPIN]['x'].append(_current)
                        self.__outputstatus[OUTPIN]['y'].append(1)
                else:
                    self.__outputstatus[OUTPIN]['y'].append(1)
            else:
                if self.__use_num_for_plot:
                    _current = self.__impulse_num
                else:
                    _current = time.time() - self.__start_time
                self.__outputstatus[OUTPIN]['x'].append(_current)

                if len(self.__outputstatus[OUTPIN]['y']) >= 1:
                    if self.__outputstatus[OUTPIN]['y'][-1] == 0:
                        self.__outputstatus[OUTPIN]['y'].append(0)
                    else:
                        self.__outputstatus[OUTPIN]['y'].append(1)
                        self.__outputstatus[OUTPIN]['x'].append(_current)
                        self.__outputstatus[OUTPIN]['y'].append(0)
                else:
                    self.__outputstatus[OUTPIN]['y'].append(0)

        if 'INPUT' in type and invector is not None:

            for k in invector:
                if k not in self.__outputstatus:
                    self.__outputstatus[k] = {'x': [], 'y': []}
                OUTPIN = k

                if invector[k]:
                    if self.__use_num_for_plot:
                        _current = self.__impulse_num
                    else:
                        _current = time.time() - self.__start_time
                    self.__outputstatus[OUTPIN]['x'].append(_current)
                    if len(self.__outputstatus[OUTPIN]['y']) >= 1:
                        if self.__outputstatus[OUTPIN]['y'][-1] == 1:
                            self.__outputstatus[OUTPIN]['y'].append(1)
                        else:
                            self.__outputstatus[OUTPIN]['y'].append(0)
                            self.__outputstatus[OUTPIN]['x'].append(_current)
                            self.__outputstatus[OUTPIN]['y'].append(1)
                    else:
                        self.__outputstatus[OUTPIN]['y'].append(1)
                else:
                    if self.__use_num_for_plot:
                        _current = self.__impulse_num
                    else:
                        _current = time.time() - self.__start_time
                    self.__outputstatus[OUTPIN]['x'].append(_current)

                    if len(self.__outputstatus[OUTPIN]['y']) >= 1:
                        if self.__outputstatus[OUTPIN]['y'][-1] == 0:
                            self.__outputstatus[OUTPIN]['y'].append(0)
                        else:
                            self.__outputstatus[OUTPIN]['y'].append(1)
                            self.__outputstatus[OUTPIN]['x'].append(_current)
                            self.__outputstatus[OUTPIN]['y'].append(0)
                    else:
                        self.__outputstatus[OUTPIN]['y'].append(0)

    def draw(self):
        plt.figure(figsize=self.figure_size)
        count = 0
        for signal in self.__outputstatus:
            count += 1
            plt.subplot(len(self.__outputstatus), 1, count)
            plt.plot(self.__outputstatus[signal]['x'], self.__outputstatus[signal]['y'])
            plt.title(signal)
        plt.show()




