#! /usr/bin/python
# -*- coding: utf-8 -*-

# The same set of code can switch the backend with one line
import os
# os.environ['TL_BACKEND'] = 'tensorflow'
# os.environ['TL_BACKEND'] = 'mindspore'
os.environ['TL_BACKEND'] = 'paddle'

import tensorlayer as tl
from tensorlayer.layers import Module
from tensorlayer.layers import Dense, Dropout
from tensorlayer.dataflow import Dataset

X_train, y_train, X_val, y_val, X_test, y_test = tl.files.load_mnist_dataset(shape=(-1, 784))


class mnistdataset(Dataset):

    def __init__(self, data=X_train, label=y_train):
        self.data = data
        self.label = label

    def __getitem__(self, index):
        data = self.data[index].astype('float32')
        label = self.label[index].astype('int64')

        return data, label

    def __len__(self):

        return len(self.data)


class CustomModel(Module):

    def __init__(self):
        super(CustomModel, self).__init__()
        self.dropout1 = Dropout(keep=0.8)
        self.dense1 = Dense(n_units=800, act=tl.ReLU, in_channels=784)
        self.dropout2 = Dropout(keep=0.8)
        self.dense2 = Dense(n_units=800, act=tl.ReLU, in_channels=800)
        self.dropout3 = Dropout(keep=0.8)
        self.dense3 = Dense(n_units=10, act=tl.ReLU, in_channels=800)

    def forward(self, x, foo=None):
        z = self.dropout1(x)
        z = self.dense1(z)
        z = self.dropout2(z)
        z = self.dense2(z)
        z = self.dropout3(z)
        out = self.dense3(z)
        if foo is not None:
            out = tl.ops.relu(out)
        return out


MLP = CustomModel()

n_epoch = 50
batch_size = 128
print_freq = 2

train_weights = MLP.trainable_weights
optimizer = tl.optimizers.Momentum(0.05, 0.9)
metric = tl.metric.Accuracy()
loss_fn = tl.cost.softmax_cross_entropy_with_logits
train_dataset = mnistdataset(data=X_train, label=y_train)
train_dataset = tl.dataflow.FromGenerator(
    train_dataset, output_types=[tl.float32, tl.int64], column_names=['data', 'label']
)
train_loader = tl.dataflow.Dataloader(train_dataset, batch_size=batch_size, shuffle=True)

model = tl.models.Model(network=MLP, loss_fn=loss_fn, optimizer=optimizer, metrics=metric)
model.train(n_epoch=n_epoch, train_dataset=train_loader, print_freq=print_freq, print_train_batch=False)
model.save_weights('./model.npz', format='npz_dict')
model.load_weights('./model.npz', format='npz_dict')
