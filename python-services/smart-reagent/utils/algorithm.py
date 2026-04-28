# version 2.0  updated in 20250918

import numpy as np
import cvxpy as cp

class ListQueue:
    def __init__(self, len):
        self.items = [0] * len
        self.size = len

    def en_queue(self, data):
        self.items.insert(0, data)
        data = self.items.pop()

    def de_queue(self):
        data = self.items.pop()
        self.size -= 1
        return data

class Controller:
    def __init__(self, dt=1, para1=5, para2=0.0, para3=1, u_min=float('-inf'), u_max=float('inf')):
        self.prev_error = 0
        self.integral = 0
        self.dt = dt
        self.para1 = para1
        self.para2 = para2
        self.para3 = para3
        self.u_min = u_min
        self.u_max = u_max
        self.prev_output = 0


    def update_FL_AntiWindup(self, setpoint, process_variable, para1, para2, para3):

        error = setpoint - process_variable
        derivative = (error - self.prev_error) / self.dt
        output_unconstrained = para1 * error + para2 * self.integral + para3 * derivative

        if (output_unconstrained >= self.u_max - 0.2 and error > 0):
            integral_adjustment = (output_unconstrained - (self.u_max - 0.2)) / (para1 / 3)
            self.integral -= integral_adjustment

        else:
            self.integral += error * self.dt

        output_adjusted = para1 * error + para2 * self.integral + para3 * derivative

        if output_adjusted > self.u_max:
            output = self.u_max
        elif output_adjusted < self.u_min:
            output = self.u_min
        else:
            output = output_adjusted

        self.prev_error = error
        self.prev_output = output

        return output

    def update_BS_AntiWindup(self, setpoint, process_variable, para1, para2, para3):

        error = -(setpoint - process_variable)
        derivative = (error - self.prev_error) / self.dt
        output_unconstrained = para1 * error + para2 * self.integral + para3 * derivative

        if (output_unconstrained >= self.u_max - 0.2 and error > 0):
            integral_adjustment = (output_unconstrained - (self.u_max - 0.2)) / (para1 / 3)
            self.integral -= integral_adjustment

        else:
            self.integral += error * self.dt

        output_adjusted = para1 * error + para2 * self.integral + para3 * derivative

        if output_adjusted > self.u_max:
            output = self.u_max
        elif output_adjusted < self.u_min:
            output = self.u_min
        else:
            output = output_adjusted

        self.prev_error = error
        self.prev_output = output

        return output

    def update_Jiayao_AntiWindup(self, setpoint, process_variable, para1, para2, para3):


        error = -(setpoint - process_variable)
        derivative = (error - self.prev_error) / self.dt
        output_unconstrained = para1 * error + para2 * self.integral + para3 * derivative

        if (output_unconstrained >= self.u_max and error > 0):
            integral_adjustment = (output_unconstrained - self.u_max) / (para1 / 3)
            self.integral -= integral_adjustment
        else:
            self.integral += error * self.dt

        output_adjusted = para1 * error + para2 * self.integral + para3 * derivative

        if output_adjusted > self.u_max:
            output = self.u_max
        elif output_adjusted < self.u_min:
            output = self.u_min
        else:
            output = output_adjusted

        self.prev_error = error
        self.prev_output = output

        print("---加药：参数1:%.2f---参数2:%.2f---参数3:%.2f---" % (para1, para2, para3))
        return output

    def updateIntegral(self):
        self.integral -= 1

    def integralVal(self):
        return self.integral

class ADRController:
    def __init__(self, b_known = -0.15, l1 = 0.02, l2 = 0.01, para1 = 0.03, setpoint = 5, dt = 1):

        self.b = b_known
        self.l1 = l1
        self.l2 = l2
        self.para1 = para1
        self.setpoint = setpoint
        self.dt = dt
        self.z1 = 0.0  # 状态估计
        self.z2 = 0.0  # 扰动估计

    def setParam(self, para1, l1, l2):
        self.l1 = l1
        self.l2 = l2
        self.para1 = para1

    def compute(self, measurement):
        e = measurement - self.z1
        # 计算控制量
        u0 = self.para1 * (self.setpoint - self.z1)
        u = (u0 - self.z2) / self.b
        # 更新ESO
        z1_dot = self.z2 + self.l1 * e + self.b * u
        z2_dot = self.l2 * e
        self.z1 += z1_dot * self.dt
        self.z2 += z2_dot * self.dt
        return u

class OnlineLSIdentifier:
    def __init__(self, n_params, delay_steps, lambda_=1.0):
        """
        参数说明：
        n_params: 待辨识参数数量 (此处为2: a, b)
        delay_steps: 已知的延迟步数
        lambda_: 遗忘因子 (默认为1，即无遗忘)
        """
        self.n_params = n_params
        self.delay_steps = delay_steps
        self.lambda_ = lambda_

        self.theta = np.zeros(n_params)

        self.P = 1e4 * np.eye(n_params)

        self.input_buffer = np.zeros(delay_steps + 1)
        self.output_buffer = [0.0]

    def update(self, u, y):
        """
        在线更新参数估计
        输入:
            u: 当前时刻输入
            y: 当前时刻输出
        返回:
            当前参数估计值 theta
        """

        self.input_buffer = np.roll(self.input_buffer, 1)
        self.input_buffer[0] = u

        if len(self.output_buffer) >= 1:
            phi = np.array([
                self.output_buffer[-1],  # y(k-1)
                self.input_buffer[-1]  # u(k-d-1)
            ])
        else:
            phi = np.zeros(self.n_params)

        K = (self.P @ phi) / (self.lambda_ + phi.T @ self.P @ phi)

        y_pred = phi.T @ self.theta
        self.theta += K * (y - y_pred)

        self.P = (self.P - np.outer(K, phi.T @ self.P)) / self.lambda_

        self.output_buffer.append(y)

        return self.theta.copy()

def yw_lowerCount(ywHist, yw_min):
    count = 0
    for i in range(len(ywHist)-1):
        if ywHist[i] >= yw_min and ywHist[i+1] < yw_min:
            count += 1
    return count

class MPCController:
    def __init__(self, dt=1, N=10, Q=50, R=1, u_min=int('0'), u_max=int('1')):

        self.dt = dt  # 采样时间
        self.N = N  # 预测时间步长
        #模型方程
        self.A = np.array([[0, 0, 0], [1, 0, 0], [0, 0.004, 0.985]])
        self.B = np.array([[1.0], [0], [0]])
        self.C = np.array([[0, 0, 1]])
        self.U_prev = np.array([[1, 0, 0]])

        self.x = cp.Variable((self.A.shape[0], N+1))
        self.u = cp.Variable((self.B.shape[1], N))
        self.u_min = u_min
        self.u_max = u_max

        self.Q = np.eye(self.B.shape[1]) * Q
        self.R = np.eye(self.B.shape[1])*R

    def updata(self, yr, measured, u_prev):
        cost = 0
        x_curr = np.array([[u_prev[-1]],[u_prev[-2]],[measured]])
        constraints = [self.x[:, 0] == x_curr[:, 0]]

        for k in range(self.N):
            if k >= 1:
                cost += cp.quad_form(self.C @ self.x[:, k] - yr, self.Q) + cp.quad_form(self.u[:, k] - self.u[:, k - 1], self.R)
            else:
                cost += cp.quad_form(self.C @ self.x[:, k] - yr, self.Q) + cp.quad_form(self.u[:, k] - self.U_prev @ self.x[:, k], self.R)
            constraints += [self.x[:, k + 1] == self.A @ self.x[:, k] + self.B @ self.u[:, k]]
            constraints += [self.u[:, k] >= self.u_min, self.u[:, k] <= self.u_max]

        prob = cp.Problem(cp.Minimize(cost), constraints)

        prob.solve()

        u_opt = self.u[:, 0].value

        return u_opt

rho_diverter_controller_3207 = Controller()
rho_water_controller_3207 = Controller()
rho_diverter_controller_3208 = Controller()
rho_water_controller_3208 = Controller()
rho_diverter_controller_316 = Controller()
rho_water_controller_316 = Controller()
jiayao_controller_601 = Controller()
jiayao_controller_602 = Controller()
jiayao_controller_5201 = Controller()
jiayao_controller_5202 = Controller()
jiayao_adrc_controller = ADRController()
identifier3207_diverter = OnlineLSIdentifier(n_params=2, delay_steps=6, lambda_=0.95)
identifier3207_water = OnlineLSIdentifier(n_params=2, delay_steps=6, lambda_=0.95)
identifier601_pump = OnlineLSIdentifier(n_params=2, delay_steps=6, lambda_=0.95)
identifier3207yw_diverter = OnlineLSIdentifier(n_params=2, delay_steps=0, lambda_=0.95)
