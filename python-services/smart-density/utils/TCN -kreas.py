#程序说明：

#这个程序是一个使用TensorFlow和Keras库构建的简单的Temporal Convolutional Network（TCN）模型。
# 它包含三个输入，每个输入都通过一个TCN层处理，然后将输出合并，并通过一个全连接层来产生两个不同的输出。以下是程序的使用方法：
# 1. 导入必要的库
# 程序开始部分导入了构建模型所需的所有Keras模块。
#
# 2. 定义TCN层
# TCNLayer函数定义了一个TCN网络层，它包括一个一维卷积层（Conv1D），后面跟着一个ReLU激活函数、
# 一个批量归一化层（BatchNormalization）。这个函数接受过滤器数量、核大小、扩张率和dropout率作为参数。
#
# 3. 构建输入层
# 程序定义了三个输入层，每个输入层都预期接收形状为(10, 1)的输入数据，即每个输入序列有10个时间步，每个时间步有1个特征。
#
# 4. 应用TCN层
# 对于每个输入，程序通过调用TCNLayer函数来应用定义的TCN层。
#
# 5. 合并输出
# 使用Concatenate层将三个TCN层的输出合并成一个单一的张量。
#
# 6. 添加Lambda层
# Lambda层在这里用来打印合并后张量的形状，以便于调试。
#
# 7. 全连接层
# 合并后的张量通过一个Flatten层展平，然后通过一个包含128个单元的全连接层（Dense），接着是一个ReLU激活函数和一个dropout层。
#
# 8. 输出层
# 模型有两个输出，每个输出都是通过一个全连接层（Dense）产生的，每个输出层有一个单元。
#
# 9. 构建和编译模型
# 使用Model类构建模型，将输入和输出连接起来。然后使用compile方法编译模型，指定优化器为adam，损失函数为mean_squared_error。
#
# 10. 打印模型结构
# 使用summary方法打印模型的结构，这将显示每层的输出形状和参数数量。
#
# 使用方法
# 要使用这个程序，你需要：
#
# 准备三个形状为(10, 1)的输入数据集。
# 将数据传递给模型的输入层。
# 调用模型的fit方法来训练模型，或者使用predict方法来进行预测。
# 示例代码（假设你已经有了数据）：

# # 假设X1, X2, X3是你的输入数据，y1和y2是目标输出
# X1, X2, X3 = ...  # 你的输入数据
# y1, y2 = ...  # 你的目标输出
#
# # 训练模型
# history = model.fit([X1, X2, X3], [y1, y2], epochs=10, batch_size=32)
#
# # 进行预测
# predictions = model.predict([X1_new, X2_new, X3_new])
# 请确保你的数据与模型的输入形状相匹配，并且你已经准备好了训练和测试数据

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Conv1D, Flatten, Dropout, Activation, BatchNormalization, Concatenate
from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Lambda

# 定义TCN层
def TCNLayer(filters, kernel_size, dilation_rate, dropout_rate, use_skip_connection=True, regularizer=l2(0.01)):
    def layer(input):
        x = Conv1D(filters=filters, kernel_size=kernel_size, dilation_rate=dilation_rate, padding='causal', kernel_regularizer=regularizer)(input)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        return x
    return layer

# 输入层
input1 = Input(shape=(10, 1), name='input1')  # 假设每个输入序列的长度为10
input2 = Input(shape=(10, 1), name='input2')
input3 = Input(shape=(10, 1), name='input3')

# TCN层
x1 = TCNLayer(64, 2, 1, 0.2)(input1)
x2 = TCNLayer(64, 2, 1, 0.2)(input2)
x3 = TCNLayer(64, 2, 1, 0.2)(input3)

# 合并输入
combined = Concatenate()([x1, x2, x3])

# 添加一个Lambda层来打印形状，以便调试
print_shape = Lambda(lambda x: x, name='print_shape')(combined)

# 全连接层
x = Flatten()(combined)
x = Dense(128, kernel_regularizer=l2(0.01))(x)
x = Activation('relu')(x)
x = Dropout(0.5)(x)

# 输出层
output1 = Dense(1, name='output1')(x)
output2 = Dense(1, name='output2')(x)

# 模型
model = Model(inputs=[input1, input2, input3], outputs=[output1, output2])

# 编译模型
model.compile(optimizer='adam', loss='mean_squared_error')

# 打印模型结构
model.summary()
