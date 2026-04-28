from skfuzzy import control as ctrl


def create_fuzzy_variables(config):
    """
    创建模糊变量：名字、论域、隶属度分级等
    :param config:
    :return:
    """
    ZDErr_config = config.get("ZDErr", {})
    PY_config = config.get("PYLevel", {})
    ZDChangeRate_config = config.get("ZDChangeRate", {})
    pumpValve_config = config.get("pumpValve", {})
    MNValve_config = config.get("MNValve", {})

    ZDErr = create_antecedent_variable(
        ZDErr_config.get("name", "ZDErr"),
        ZDErr_config.get("universe_l", -1),
        ZDErr_config.get("universe_r", 1),
        ZDErr_config.get("num_intervals", 5),
        ZDErr_config.get("is_trapmf", False)
    )

    PYLevel = create_antecedent_variable(
        PY_config.get("name", "PYLevel"),
        PY_config.get("universe_l", 0),
        PY_config.get("universe_r", 1),
        PY_config.get("num_intervals", 3),
        PY_config.get("is_trapmf", False)
    )

    ZDChangeRate = create_antecedent_variable(
        ZDChangeRate_config.get("name", "ZDChangeRate"),
        ZDChangeRate_config.get("universe_l", -1),
        ZDChangeRate_config.get("universe_r", 1),
        ZDChangeRate_config.get("num_intervals", 5),
        ZDChangeRate_config.get("is_trapmf", False)
    )

    pumpValve = create_consequent_variable(
        pumpValve_config.get("name", "pumpValve"),
        pumpValve_config.get("universe_l", 0),
        pumpValve_config.get("universe_r", 1),
        pumpValve_config.get("num_intervals", 5)
    )

    MNValve = create_consequent_variable(
        MNValve_config.get("name", "MNValve"),
        MNValve_config.get("universe_l", 0),
        MNValve_config.get("universe_r", 1),
        MNValve_config.get("num_intervals", 5)
    )

    return ZDErr, PYLevel, ZDChangeRate, pumpValve, MNValve


def create_antecedent_variable(name, universe_l, universe_r, num_intervals, is_trapmf=False):
    """
    创建模糊前件变量，并自动生成隶属度函数

    参数:
    name (str): 变量名称
    universe_l (float): 论域的左边界
    universe_r (float): 论域的右边界
    num_intervals (int): 划分的区间数量（用于确定隶属度函数个数）
    is_trapmf (bool): 是否使用梯形隶属度函数（默认False使用三角形隶属度函数）

    返回:
    ctrl.Antecedent: 创建好的模糊前件变量对象
    """
    universe = np.arange(universe_l, universe_r, (universe_r - universe_l) / 1000)  # 精细划分论域
    var = ctrl.Antecedent(universe, name)
    interval_width = (universe_r - universe_l) / num_intervals
    for i in range(num_intervals):
        if is_trapmf:
            left = universe_l + i * interval_width
            right = universe_l + (i + 1) * interval_width
            if i == 0:
                left_l = left
                left_r = left
            else:
                left_l = universe_l + (i - 1) * interval_width
            if i == num_intervals - 1:
                right_l = right
                right_r = right
            else:
                right_r = universe_l + (i + 2) * interval_width
            label = get_label(i, num_intervals)
            var[label] = fuzz.trapmf(var.universe, [left_l, left, right, right_r])
        else:
            center = universe_l + (i + 0.5) * interval_width
            left = center - interval_width / 2
            right = center + interval_width / 2
            label = get_label(i, num_intervals)
            var[label] = fuzz.trimf(var.universe, [left, center, right])
    return var


def create_consequent_variable(name, universe_l, universe_r, num_intervals):
    """
    创建模糊后件变量，并自动生成隶属度函数

    参数:
    name (str): 变量名称
    universe_l (float): 论域的左边界
    universe_r (float): 论域的右边界
    num_intervals (int): 划分的区间数量（用于确定隶属度函数个数）

    返回:
    ctrl.Consequent: 创建好的模糊后件变量对象
    """
    universe = np.arange(universe_l, universe_r, (universe_r - universe_l) / 1000)  # 精细划分论域
    var = ctrl.Consequent(universe, name)
    interval_width = (universe_r - universe_l) / num_intervals
    for i in range(num_intervals):
        center = universe_l + (i + 0.5) * interval_width
        left = center - interval_width / 2
        right = center + interval_width / 2
        label = get_label(i, num_intervals)
        var[label] = fuzz.trimf(var.universe, [left, center, right])
    return var


def get_label(index, num_intervals):
    """
    根据索引和区间数量生成隶属度函数的标签

    参数:
    index (int): 当前区间的索引
    num_intervals (int): 总的区间数量

    返回:
    str: 隶属度函数的标签，如'NB'、'NM'等
    """
    labels = ['NB', 'NM', 'NS', 'ZO', 'PS', 'PM', 'PB']
    if num_intervals == 3:
        labels = ['NB', 'ZO', 'PB']
    elif num_intervals == 5:
        labels = ['NB', 'NS', 'ZO', 'PS', 'PB']
    return labels[index]

def _clamp(value, limits):
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


class PID(object):
    """A simple PID controller."""

    def __init__(
        self,
        Kp=1.0,
        Ki=0.0,
        Kd=0.0,
        setpoint=0,
        sample_time=1,
        output_limits=(None, None),
        auto_mode=True,
        proportional_on_measurement=False,
        differential_on_measurement=True,
        error_map=None,
        time_fn=None,
        starting_output=0.0,
    ):
        """
        Initialize a new PID controller.

        :param Kp: The value for the proportional gain Kp
        :param Ki: The value for the integral gain Ki
        :param Kd: The value for the derivative gain Kd
        :param setpoint: The initial setpoint that the PID will try to achieve
        :param sample_time: The time in seconds which the controller should wait before generating
            a new output value. The PID works best when it is constantly called (eg. during a
            loop), but with a sample time set so that the time difference between each update is
            (close to) constant. If set to None, the PID will compute a new output value every time
            it is called.
        :param output_limits: The initial output limits to use, given as an iterable with 2
            elements, for example: (lower, upper). The output will never go below the lower limit
            or above the upper limit. Either of the limits can also be set to None to have no limit
            in that direction. Setting output limits also avoids integral windup, since the
            integral term will never be allowed to grow outside of the limits.
        :param auto_mode: Whether the controller should be enabled (auto mode) or not (manual mode)
        :param proportional_on_measurement: Whether the proportional term should be calculated on
            the input directly rather than on the error (which is the traditional way). Using
            proportional-on-measurement avoids overshoot for some types of systems.
        :param differential_on_measurement: Whether the differential term should be calculated on
            the input directly rather than on the error (which is the traditional way).
        :param error_map: Function to transform the error value in another constrained value.
        :param time_fn: The function to use for getting the current time, or None to use the
            default. This should be a function taking no arguments and returning a number
            representing the current time. The default is to use time.monotonic() if available,
            otherwise time.time().
        :param starting_output: The starting point for the PID's output. If you start controlling
            a system that is already at the setpoint, you can set this to your best guess at what
            output the PID should give when first calling it to avoid the PID outputting zero and
            moving the system away from the setpoint.
        """
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self.sample_time = sample_time

        self._min_output, self._max_output = None, None
        self._auto_mode = auto_mode
        self.proportional_on_measurement = proportional_on_measurement
        self.differential_on_measurement = differential_on_measurement
        self.error_map = error_map

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._last_time = None
        self._last_output = None
        self._last_error = None
        self._last_input = None

        if time_fn is not None:
            # Use the user supplied time function
            self.time_fn = time_fn
        else:
            import time

            try:
                # Get monotonic time to ensure that time deltas are always positive
                self.time_fn = time.monotonic
            except AttributeError:
                # time.monotonic() not available (using python < 3.3), fallback to time.time()
                self.time_fn = time.time

        self.output_limits = output_limits
        self.reset()

        # Set initial state of the controller
        self._integral = _clamp(starting_output, output_limits)

    def __call__(self, input_, dt=None):
        """
        Update the PID controller.

        Call the PID controller with *input_* and calculate and return a control output if
        sample_time seconds has passed since the last update. If no new output is calculated,
        return the previous output instead (or None if no value has been calculated yet).

        :param dt: If set, uses this value for timestep instead of real time. This can be used in
            simulations when simulation time is different from real time.
        """
        if not self.auto_mode:
            return self._last_output

        now = self.time_fn()
        if dt is None:
            dt = now - self._last_time if (now - self._last_time) else 1e-16
        elif dt <= 0:
            raise ValueError('dt has negative value {}, must be positive'.format(dt))

        if self.sample_time is not None and dt < self.sample_time and self._last_output is not None:
            # Only update every sample_time seconds
            return self._last_output

        # Compute error terms
        error = self.setpoint - input_
        d_input = input_ - (self._last_input if (self._last_input is not None) else input_)
        d_error = error - (self._last_error if (self._last_error is not None) else error)

        # Check if must map the error
        if self.error_map is not None:
            error = self.error_map(error)

        # Compute the proportional term
        if not self.proportional_on_measurement:
            # Regular proportional-on-error, simply set the proportional term
            self._proportional = self.Kp * error
        else:
            # Add the proportional error on measurement to error_sum
            self._proportional -= self.Kp * d_input

        # Compute integral and derivative terms
        self._integral += self.Ki * error * dt
        self._integral = _clamp(self._integral, self.output_limits)  # Avoid integral windup

        if self.differential_on_measurement:
            self._derivative = -self.Kd * d_input / dt
        else:
            self._derivative = self.Kd * d_error / dt

        # Compute final output
        output = self._proportional + self._integral + self._derivative
        output = _clamp(output, self.output_limits)

        # Keep track of state
        self._last_output = output
        self._last_input = input_
        self._last_error = error
        self._last_time = now

        return output

    def __repr__(self):
        return (
            '{self.__class__.__name__}('
            'Kp={self.Kp!r}, Ki={self.Ki!r}, Kd={self.Kd!r}, '
            'setpoint={self.setpoint!r}, sample_time={self.sample_time!r}, '
            'output_limits={self.output_limits!r}, auto_mode={self.auto_mode!r}, '
            'proportional_on_measurement={self.proportional_on_measurement!r}, '
            'differential_on_measurement={self.differential_on_measurement!r}, '
            'error_map={self.error_map!r}'
            ')'
        ).format(self=self)

    @property
    def components(self):
        """
        The P-, I- and D-terms from the last computation as separate components as a tuple. Useful
        for visualizing what the controller is doing or when tuning hard-to-tune systems.
        """
        return self._proportional, self._integral, self._derivative

    @property
    def tunings(self):
        """The tunings used by the controller as a tuple: (Kp, Ki, Kd)."""
        return self.Kp, self.Ki, self.Kd

    @tunings.setter
    def tunings(self, tunings):
        """Set the PID tunings."""
        self.Kp, self.Ki, self.Kd = tunings

    @property
    def auto_mode(self):
        """Whether the controller is currently enabled (in auto mode) or not."""
        return self._auto_mode

    @auto_mode.setter
    def auto_mode(self, enabled):
        """Enable or disable the PID controller."""
        self.set_auto_mode(enabled)

    def set_auto_mode(self, enabled, last_output=None):
        """
        Enable or disable the PID controller, optionally setting the last output value.

        This is useful if some system has been manually controlled and if the PID should take over.
        In that case, disable the PID by setting auto mode to False and later when the PID should
        be turned back on, pass the last output variable (the control variable) and it will be set
        as the starting I-term when the PID is set to auto mode.

        :param enabled: Whether auto mode should be enabled, True or False
        :param last_output: The last output, or the control variable, that the PID should start
            from when going from manual mode to auto mode. Has no effect if the PID is already in
            auto mode.
        """
        if enabled and not self._auto_mode:
            # Switching from manual mode to auto, reset
            self.reset()

            self._integral = last_output if (last_output is not None) else 0
            self._integral = _clamp(self._integral, self.output_limits)

        self._auto_mode = enabled

    @property
    def output_limits(self):
        """
        The current output limits as a 2-tuple: (lower, upper).

        See also the *output_limits* parameter in :meth:`PID.__init__`.
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """Set the output limits."""
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits

        if (None not in limits) and (max_output < min_output):
            raise ValueError('lower limit must be less than upper limit')

        self._min_output = min_output
        self._max_output = max_output

        self._integral = _clamp(self._integral, self.output_limits)
        self._last_output = _clamp(self._last_output, self.output_limits)

    def reset(self):
        """
        Reset the PID controller internals.

        This sets each term to 0 as well as clearing the integral, the last output and the last
        input (derivative calculation).
        """
        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._integral = _clamp(self._integral, self.output_limits)

        self._last_time = self.time_fn()
        self._last_output = None
        self._last_input = None
        self._last_error = None


class PID_BS(object):
    """A simple PID controller."""

    def __init__(
        self,
        Kp=1.0,
        Ki=0.0,
        Kd=0.0,
        setpoint=0,
        sample_time=1,
        output_limits=(None, None),
        auto_mode=True,
        proportional_on_measurement=False,
        differential_on_measurement=True,
        error_map=None,
        time_fn=None,
        starting_output=0.0,
    ):
        """
        Initialize a new PID controller.

        :param Kp: The value for the proportional gain Kp
        :param Ki: The value for the integral gain Ki
        :param Kd: The value for the derivative gain Kd
        :param setpoint: The initial setpoint that the PID will try to achieve
        :param sample_time: The time in seconds which the controller should wait before generating
            a new output value. The PID works best when it is constantly called (eg. during a
            loop), but with a sample time set so that the time difference between each update is
            (close to) constant. If set to None, the PID will compute a new output value every time
            it is called.
        :param output_limits: The initial output limits to use, given as an iterable with 2
            elements, for example: (lower, upper). The output will never go below the lower limit
            or above the upper limit. Either of the limits can also be set to None to have no limit
            in that direction. Setting output limits also avoids integral windup, since the
            integral term will never be allowed to grow outside of the limits.
        :param auto_mode: Whether the controller should be enabled (auto mode) or not (manual mode)
        :param proportional_on_measurement: Whether the proportional term should be calculated on
            the input directly rather than on the error (which is the traditional way). Using
            proportional-on-measurement avoids overshoot for some types of systems.
        :param differential_on_measurement: Whether the differential term should be calculated on
            the input directly rather than on the error (which is the traditional way).
        :param error_map: Function to transform the error value in another constrained value.
        :param time_fn: The function to use for getting the current time, or None to use the
            default. This should be a function taking no arguments and returning a number
            representing the current time. The default is to use time.monotonic() if available,
            otherwise time.time().
        :param starting_output: The starting point for the PID's output. If you start controlling
            a system that is already at the setpoint, you can set this to your best guess at what
            output the PID should give when first calling it to avoid the PID outputting zero and
            moving the system away from the setpoint.
        """
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self.sample_time = sample_time

        self._min_output, self._max_output = None, None
        self._auto_mode = auto_mode
        self.proportional_on_measurement = proportional_on_measurement
        self.differential_on_measurement = differential_on_measurement
        self.error_map = error_map

        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._last_time = None
        self._last_output = None
        self._last_error = None
        self._last_input = None

        if time_fn is not None:
            # Use the user supplied time function
            self.time_fn = time_fn
        else:
            import time

            try:
                # Get monotonic time to ensure that time deltas are always positive
                self.time_fn = time.monotonic
            except AttributeError:
                # time.monotonic() not available (using python < 3.3), fallback to time.time()
                self.time_fn = time.time

        self.output_limits = output_limits
        self.reset()

        # Set initial state of the controller
        self._integral = _clamp(starting_output, output_limits)

    def __call__(self, input_, dt=None):
        """
        Update the PID controller.

        Call the PID controller with *input_* and calculate and return a control output if
        sample_time seconds has passed since the last update. If no new output is calculated,
        return the previous output instead (or None if no value has been calculated yet).

        :param dt: If set, uses this value for timestep instead of real time. This can be used in
            simulations when simulation time is different from real time.
        """
        if not self.auto_mode:
            return self._last_output

        now = self.time_fn()
        if dt is None:
            dt = now - self._last_time if (now - self._last_time) else 1e-16
        elif dt <= 0:
            raise ValueError('dt has negative value {}, must be positive'.format(dt))

        if self.sample_time is not None and dt < self.sample_time and self._last_output is not None:
            # Only update every sample_time seconds
            return self._last_output

        # Compute error terms
        error = -1*(self.setpoint - input_)
        d_input = input_ - (self._last_input if (self._last_input is not None) else input_)
        d_error = error - (self._last_error if (self._last_error is not None) else error)

        # Check if must map the error
        if self.error_map is not None:
            error = self.error_map(error)

        # Compute the proportional term
        if not self.proportional_on_measurement:
            # Regular proportional-on-error, simply set the proportional term
            self._proportional = self.Kp * error
        else:
            # Add the proportional error on measurement to error_sum
            self._proportional -= self.Kp * d_input

        # Compute integral and derivative terms
        self._integral += self.Ki * error * dt
        self._integral = _clamp(self._integral, self.output_limits)  # Avoid integral windup

        if self.differential_on_measurement:
            self._derivative = -self.Kd * d_input / dt
        else:
            self._derivative = self.Kd * d_error / dt

        # Compute final output
        output = self._proportional + self._integral + self._derivative
        output = _clamp(output, self.output_limits)

        # Keep track of state
        self._last_output = output
        self._last_input = input_
        self._last_error = error
        self._last_time = now

        return output

    def __repr__(self):
        return (
            '{self.__class__.__name__}('
            'Kp={self.Kp!r}, Ki={self.Ki!r}, Kd={self.Kd!r}, '
            'setpoint={self.setpoint!r}, sample_time={self.sample_time!r}, '
            'output_limits={self.output_limits!r}, auto_mode={self.auto_mode!r}, '
            'proportional_on_measurement={self.proportional_on_measurement!r}, '
            'differential_on_measurement={self.differential_on_measurement!r}, '
            'error_map={self.error_map!r}'
            ')'
        ).format(self=self)

    @property
    def components(self):
        """
        The P-, I- and D-terms from the last computation as separate components as a tuple. Useful
        for visualizing what the controller is doing or when tuning hard-to-tune systems.
        """
        return self._proportional, self._integral, self._derivative

    @property
    def tunings(self):
        """The tunings used by the controller as a tuple: (Kp, Ki, Kd)."""
        return self.Kp, self.Ki, self.Kd

    @tunings.setter
    def tunings(self, tunings):
        """Set the PID tunings."""
        self.Kp, self.Ki, self.Kd = tunings

    @property
    def auto_mode(self):
        """Whether the controller is currently enabled (in auto mode) or not."""
        return self._auto_mode

    @auto_mode.setter
    def auto_mode(self, enabled):
        """Enable or disable the PID controller."""
        self.set_auto_mode(enabled)

    def set_auto_mode(self, enabled, last_output=None):
        """
        Enable or disable the PID controller, optionally setting the last output value.

        This is useful if some system has been manually controlled and if the PID should take over.
        In that case, disable the PID by setting auto mode to False and later when the PID should
        be turned back on, pass the last output variable (the control variable) and it will be set
        as the starting I-term when the PID is set to auto mode.

        :param enabled: Whether auto mode should be enabled, True or False
        :param last_output: The last output, or the control variable, that the PID should start
            from when going from manual mode to auto mode. Has no effect if the PID is already in
            auto mode.
        """
        if enabled and not self._auto_mode:
            # Switching from manual mode to auto, reset
            self.reset()

            self._integral = last_output if (last_output is not None) else 0
            self._integral = _clamp(self._integral, self.output_limits)

        self._auto_mode = enabled

    @property
    def output_limits(self):
        """
        The current output limits as a 2-tuple: (lower, upper).

        See also the *output_limits* parameter in :meth:`PID.__init__`.
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """Set the output limits."""
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits

        if (None not in limits) and (max_output < min_output):
            raise ValueError('lower limit must be less than upper limit')

        self._min_output = min_output
        self._max_output = max_output

        self._integral = _clamp(self._integral, self.output_limits)
        self._last_output = _clamp(self._last_output, self.output_limits)

    def reset(self):
        """
        Reset the PID controller internals.

        This sets each term to 0 as well as clearing the integral, the last output and the last
        input (derivative calculation).
        """
        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        self._integral = _clamp(self._integral, self.output_limits)

        self._last_time = self.time_fn()
        self._last_output = None
        self._last_input = None
        self._last_error = None

rule1 = ctrl.Rule(ZDErr['NB'] & ZDChangeRate['NB'], pumpValve['PB'])
rule2 = ctrl.Rule(ZDErr['NB'] & ZDChangeRate['NS'], pumpValve['PB'])
rule3 = ctrl.Rule(ZDErr['NB'] & ZDChangeRate['ZO'], pumpValve['PB'])
rule4 = ctrl.Rule(ZDErr['NB'] & ZDChangeRate['PS'], pumpValve['PS'])
rule5 = ctrl.Rule(ZDErr['NB'] & ZDChangeRate['PB'], pumpValve['PS'])

rule6 = ctrl.Rule(ZDErr['NM'] & ZDChangeRate['NB'], pumpValve['PB'])
rule7 = ctrl.Rule(ZDErr['NM'] & ZDChangeRate['NS'], pumpValve['PB'])
rule8 = ctrl.Rule(ZDErr['NM'] & ZDChangeRate['ZO'], pumpValve['PB'])
rule9 = ctrl.Rule(ZDErr['NM'] & ZDChangeRate['PS'], pumpValve['PS'])
rule10 = ctrl.Rule(ZDErr['NM'] & ZDChangeRate['PB'], pumpValve['PS'])

rule11 = ctrl.Rule(ZDErr['NS'] & ZDChangeRate['NB'], pumpValve['PB'])
rule12 = ctrl.Rule(ZDErr['NS'] & ZDChangeRate['NS'], pumpValve['PB'])
rule13 = ctrl.Rule(ZDErr['NS'] & ZDChangeRate['ZO'], pumpValve['PS'])
rule14 = ctrl.Rule(ZDErr['NS'] & ZDChangeRate['PS'], pumpValve['PS'])
rule15 = ctrl.Rule(ZDErr['NS'] & ZDChangeRate['PB'], pumpValve['NS'])

rule16 = ctrl.Rule(ZDErr['ZO'] & ZDChangeRate['NB'], pumpValve['PB'])
rule17 = ctrl.Rule(ZDErr['ZO'] & ZDChangeRate['NS'], pumpValve['PS'])
rule18 = ctrl.Rule(ZDErr['ZO'] & ZDChangeRate['ZO'], pumpValve['ZO'])
rule19 = ctrl.Rule(ZDErr['ZO'] & ZDChangeRate['PS'], pumpValve['NS'])
rule20 = ctrl.Rule(ZDErr['ZO'] & ZDChangeRate['PB'], pumpValve['NB'])

rule21 = ctrl.Rule(ZDErr['PS'] & ZDChangeRate['NB'], pumpValve['PS'])
rule22 = ctrl.Rule(ZDErr['PS'] & ZDChangeRate['NS'], pumpValve['PS'])
rule23 = ctrl.Rule(ZDErr['PS'] & ZDChangeRate['ZO'], pumpValve['NS'])
rule24 = ctrl.Rule(ZDErr['PS'] & ZDChangeRate['PS'], pumpValve['NS'])
rule25 = ctrl.Rule(ZDErr['PS'] & ZDChangeRate['PB'], pumpValve['NB'])

fuzzy_sys1 = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
                                          rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20,
                                          rule21, rule22, rule23, rule24, rule25])
fuzzy_sim1 = ctrl.ControlSystemSimulation(fuzzy_sys)

fuzzy_sys2 = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
                                          rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20,
                                          rule21, rule22, rule23, rule24, rule25])
fuzzy_sim2 = ctrl.ControlSystemSimulation(fuzzy_sys)

fuzzy_sys3 = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
                                          rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20,
                                          rule21, rule22, rule23, rule24, rule25])
fuzzy_sim3 = ctrl.ControlSystemSimulation(fuzzy_sys)

fuzzy_sys4 = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
                                          rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20,
                                          rule21, rule22, rule23, rule24, rule25])
fuzzy_sim4 = ctrl.ControlSystemSimulation(fuzzy_sys)

res_pump = np.zeros(inputIntervel.shape[0])
res_MN = np.zeros(inputIntervel.shape[0])
for i in range(inputIntervel.shape[0]):
    # 给定输入（密度偏差、密度偏差变化率、液位）
    fuzzy_sim_diverter.input['ZDErr'] = inputIntervel[i, 4]
    fuzzy_sim_diverter.input['ZDChangeRate'] = inputIntervel[i, 5]

    fuzzy_sim1.compute()
    res_pump[i] = fuzzy_sim1.output['pumpValve']
    res_pump[i] = round(res_pump[i])
    print("control: %d || real: %d\n" % (res_pump[i], inputIntervel[i, 1]))

res_pump = np.zeros(inputIntervel.shape[0])
res_MN = np.zeros(inputIntervel.shape[0])
for i in range(inputIntervel.shape[0]):
    # 给定输入（密度偏差、密度偏差变化率、液位）
    fuzzy_sim_diverter.input['ZDErr'] = inputIntervel[i, 4]
    fuzzy_sim_diverter.input['ZDChangeRate'] = inputIntervel[i, 5]

    fuzzy_sim1.compute()
    res_pump[i] = fuzzy_sim2.output['pumpValve']
    res_pump[i] = round(res_pump[i])
    print("control: %d || real: %d\n" % (res_pump[i], inputIntervel[i, 1]))

res_pump = np.zeros(inputIntervel.shape[0])
res_MN = np.zeros(inputIntervel.shape[0])
for i in range(inputIntervel.shape[0]):
    # 给定输入（密度偏差、密度偏差变化率、液位）
    fuzzy_sim_diverter.input['ZDErr'] = inputIntervel[i, 4]
    fuzzy_sim_diverter.input['ZDChangeRate'] = inputIntervel[i, 5]

    fuzzy_sim1.compute()
    res_pump[i] = fuzzy_sim3.output['pumpValve']
    res_pump[i] = round(res_pump[i])
    print("control: %d || real: %d\n" % (res_pump[i], inputIntervel[i, 1]))

res_pump = np.zeros(inputIntervel.shape[0])
res_MN = np.zeros(inputIntervel.shape[0])
for i in range(inputIntervel.shape[0]):
    # 给定输入（密度偏差、密度偏差变化率、液位）
    fuzzy_sim_diverter.input['ZDErr'] = inputIntervel[i, 4]
    fuzzy_sim_diverter.input['ZDChangeRate'] = inputIntervel[i, 5]

    fuzzy_sim1.compute()
    res_pump[i] = fuzzy_sim4.output['pumpValve']
    res_pump[i] = round(res_pump[i])
    print("control: %d || real: %d\n" % (res_pump[i], inputIntervel[i, 1]))

jiayao_controller_601 = FuzzyPIDController()
jiayao_controller_602 = FuzzyPIDController()
jiayao_controller_5201 = FuzzyPIDController()
jiayao_controller_5202 = FuzzyPIDController()