import torch
import csv

import torch.nn as nn
import torch.optim as optim
import numpy as np

from torch.utils.data import Dataset, DataLoader, SubsetRandomSampler

#############################################################################################################################################################################################################
##############################################################################################                 ##############################################################################################
#############################################################################################                   #############################################################################################
############################################################################################  CLASS FOR DATASET  ############################################################################################
#############################################################################################                   #############################################################################################
##############################################################################################                 ##############################################################################################
#############################################################################################################################################################################################################

class Project3Dataset(Dataset):
  def __init__(self, filename, dense_2_out_feature_size):
    self.ship_layouts, self.probability_matrices, self.bot_positions, self.actions = fetch_data(filename, dense_2_out_feature_size)
    self.grid_size = self.ship_layouts.shape[1]

  def __len__(self):
    return len(self.ship_layouts)

  def __getitem__(self, idx):
    ship_layout = self.ship_layouts[idx]
    prob_matrix = self.probability_matrices[idx]
    bot_position = self.bot_positions[idx]

    action = torch.Tensor(self.actions[idx])
    data = torch.stack([torch.Tensor(ship_layout), torch.Tensor(prob_matrix), torch.Tensor(bot_position)])

    return data, action

#############################################################################################################################################################################################################
########################################################################################                             ########################################################################################
#######################################################################################                               #######################################################################################
######################################################################################         CLASS FOR MODEL         ######################################################################################
#######################################################################################                               #######################################################################################
########################################################################################                             ########################################################################################
#############################################################################################################################################################################################################

class Project3Model(nn.Module):
  def __init__(self, grid_size, in_channel_size, conv_1_out_channel_size, conv_2_out_channel_size, dense_1_out_feature_size, dense_2_out_feature_size, kernal, stride_size, padding_size):
    super(Project3Model, self).__init__()

    self.conv_1 = torch.nn.Conv2d(in_channel_size, conv_1_out_channel_size, (kernal, kernal), stride_size, padding_size, bias = True)
    self.conv_2 = torch.nn.Conv2d(conv_1_out_channel_size, conv_2_out_channel_size, (kernal, kernal), stride_size, padding_size, bias = True)

    self.tanh = torch.nn.Tanh()
    self.sigmoid = torch.nn.Sigmoid()

    self.flatten = torch.nn.Flatten()

    self.dense_1 = torch.nn.Linear(conv_2_out_channel_size * grid_size * grid_size, dense_1_out_feature_size, True)
    self.dense_2 = torch.nn.Linear(dense_1_out_feature_size, dense_2_out_feature_size, True)

    self.relu = torch.nn.ReLU()

    self.grid_size = grid_size
    self.in_channel_size = in_channel_size

  def forward(self, input_tensor):
    reshaped = torch.reshape(input_tensor, (-1, self.in_channel_size, self.grid_size, self.grid_size))

    conv_1_results = self.conv_1(reshaped)
    tanh_results = self.tanh(conv_1_results)

    conv_2_results = self.conv_2(tanh_results)
    sigmoid_results = self.sigmoid(conv_2_results)

    flattened = self.flatten(sigmoid_results)

    linear_1_results = self.dense_1(flattened)
    relu_results = self.relu(linear_1_results)

    linear_2_results = self.dense_2(relu_results)
    logits = linear_2_results

    return logits

#############################################################################################################################################################################################################
########################################################################################                             ########################################################################################
#######################################################################################                               #######################################################################################
######################################################################################  FUNCTION FOR CONFUSION MATRIX  ######################################################################################
#######################################################################################                               #######################################################################################
########################################################################################                             ########################################################################################
#############################################################################################################################################################################################################

def confusion_matrix(model, data_loader):
  model.eval()

  number_of_classes = data_loader.dataset.actions.shape[1]
  identification_counts = np.zeros(shape = (number_of_classes, number_of_classes), dtype = np.int32)
  correct_counts = np.zeros(shape = (number_of_classes, number_of_classes), dtype = np.int32)

  for data, action in data_loader:
    logits = model(data)
    predicted_classes = torch.argmax(logits, dim = 1)
    actual_classes = torch.argmax(action, dim = 1)

    for i in range(data.shape[0]):
      actual_class = actual_classes[i].item()
      predicted_class = predicted_classes[i].item()
      identification_counts[actual_class, predicted_class] += 1
      correct_counts[actual_class, actual_class] += 1

  total_correct = 0

  for i in range(action.shape[1]):
    total_correct += identification_counts[i, i]

  accuracy = total_correct / np.sum(identification_counts)

  return identification_counts, correct_counts, accuracy

#############################################################################################################################################################################################################
########################################################################################                             ########################################################################################
#######################################################################################                               #######################################################################################
######################################################################################     FUNCTION TO FETCH DATA      ######################################################################################
#######################################################################################                               #######################################################################################
########################################################################################                             ########################################################################################
#############################################################################################################################################################################################################

def fetch_data(filename, dense_2_out_feature_size):
  ship_layouts = []
  probability_matrices = []
  bot_positions = []
  actions = []

  with open(filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)

    if reader.fieldnames != ['ship_layout', 'probability_matrix', 'bot_position', 'sense', 'action']: # Remove sense when data.csv is updated.
      raise Exception('CSV file is not formatted correctly.')

    for row in reader:
      ship_layout = eval(row['ship_layout'])
      ship_layouts.append(ship_layout)

      probability_matrix = eval(row['probability_matrix'])
      probability_matrices.append(probability_matrix)

      bot_position = eval(row['bot_position'])
      bot_positions.append(bot_position)

      action = int(row['action'])
      action_one_hot = np.zeros(dense_2_out_feature_size)
      action_one_hot[action] = 1
      actions.append(action_one_hot)

    if not len(ship_layouts) == len(probability_matrices) == len(bot_positions) == len(actions):
      raise Exception('Data not formatted correctly.')
    else:
      return (np.array(ship_layouts), 
              np.array(probability_matrices), 
              np.array(bot_positions), 
              np.array(actions))

#############################################################################################################################################################################################################
########################################################################################                             ########################################################################################
#######################################################################################                               #######################################################################################
######################################################################################          MAIN FUNCTION          ######################################################################################
#######################################################################################                               #######################################################################################
########################################################################################                             ########################################################################################
#############################################################################################################################################################################################################

def main():
  print('Defining parameters...')

  filename = 'data.csv'
  in_channel_size = 3
  conv_1_out_channel_size = 18
  conv_2_out_channel_size = 100
  dense_1_out_feature_size = 20
  dense_2_out_feature_size = 5
  kernal = 3
  stride_size = 1
  padding_size = 1
  train_data_percentage = 0.8
  val_data_out_of_test_data_percentage = 0.8
  sgd_learning_rate = 0.01
  adam_learning_rate = 0.01
  rmsprop_learning_rate = 0.01
  batch_size = 128
  epochs = 10

  if in_channel_size != 3:
    return print('Warning: In channel size is not 3.')
  elif dense_2_out_feature_size != 5:
    return print('Warning: Final out feature size is not 5.')
  elif train_data_percentage == 1:
    return print('Warning: All data will be used for training.')
  elif val_data_out_of_test_data_percentage == 1:
    return print('Warning: All test data will be used for validation.')
  elif sgd_learning_rate == 0:
    return print('Warning: SGD learning rate is set to 0. No learning rate will be used for SGD optimizer.')
  elif adam_learning_rate == 0:
    return print('Warning: Adam learning rate is set to 0. No learning rate will be used for Adam optimizer.')
  elif rmsprop_learning_rate == 0:
    return print('Warning: RMSprop learning rate is set to 0. No learning rate will be used for RMSprop optimizer.')
  elif batch_size == 0:
    return print('Warning: Batch size is set to 0. No batch training will be performed.')
  elif epochs == 0:
    return print('Warning: Epochs is set to 0. No training will be performed.')
  else:
    print('Parameters defined. Fetching data...')

  dataset = Project3Dataset(filename, dense_2_out_feature_size)
  grid_size = dataset.grid_size


# Delete later:
  print('Dataset Ship Layouts Shape:', dataset.ship_layouts.shape, '\nDataset Probability Matrices Shape:', dataset.probability_matrices.shape, '\nDataset Bot Positions Shape:', dataset.bot_positions.shape, '\nDataset Actions Shape:', dataset.actions.shape)


  if kernal > grid_size:
    return print(f'Warning: Kernal size of {kernal} is greater than grid size of {grid_size}.')
  else:
    print('Data fetched. Splitting data...')

  dataset_size = len(dataset)


# Delete later:
  print('Dataset Size:', dataset_size)


  if batch_size > dataset_size:
    return print(f'Warning: Batch size of {batch_size} is greater than dataset size of {dataset_size}.')

  indices = list(range(dataset_size))
  split = int(np.floor(train_data_percentage * dataset_size))
  train_indices, test_indices = indices[:split], indices[split:]
  split_val = int(np.floor((1 - val_data_out_of_test_data_percentage) * len(test_indices)))
  test_indices, val_indices = test_indices[:split_val], test_indices[split_val:]


# Delete later:
  print('Train Indices Length:', len(train_indices), '\nVal Indices Length:', len(val_indices), '\nTest Indices Length:', len(test_indices), '\nTotal Indices Length:', len(indices))


  print('Data split. Creating data samplers...')

  train_sampler = SubsetRandomSampler(train_indices)
  test_sampler = SubsetRandomSampler(test_indices)
  val_sampler = SubsetRandomSampler(val_indices)


# Delete later:
  print('Train Sampler Length:', len(train_sampler), '\nVal Sampler Length:', len(val_sampler), '\nTest Sampler Length:', len(test_sampler), '\nTotal Sampler Length:', len(train_sampler) + len(val_sampler) + len(test_sampler))


  print('Samplers created. Loading data...')

  train_loader = DataLoader(dataset, batch_size, sampler = train_sampler)  
  val_loader = DataLoader(dataset, batch_size, sampler = val_sampler)
  test_loader = DataLoader(dataset, batch_size, sampler = test_sampler)


# Delete later:
  print('Train Loader Length:', len(train_loader), '\nVal Loader Length:', len(val_loader), '\nTest Loader Length:', len(test_loader), '\nTotal Loader Length:', len(train_loader) + len(val_loader) + len(test_loader))


  if len(train_loader) == 0:
    return print('Warning: No data in train loader. No training will be performed.')
  if len(val_loader) == 0:
    return print('Warning: No data in validation loader. No validation will be performed.')
  if len(test_loader) == 0:
    return print('Warning: No data in test loader. No validation will be performed.')

  print('Data loaded. Creating model...')

  model = Project3Model(grid_size, in_channel_size, conv_1_out_channel_size, conv_2_out_channel_size, dense_1_out_feature_size, dense_2_out_feature_size, kernal, stride_size, padding_size)

  if model == None:
    return print('Warning: Model was not created. No model will be trained.')

  loss_function = nn.CrossEntropyLoss()
  optimizers = {'SGD': optim.SGD(model.parameters(), sgd_learning_rate),
                'Adam': optim.Adam(model.parameters(), adam_learning_rate),
                'RMSprop': optim.RMSprop(model.parameters(), rmsprop_learning_rate)}

  print('Model created. Training model...')

  best_val_accuracy = 0
  best_train_accuracy = 0
  best_model = None
  best_optimizer = None

  for optimizer_name, optimizer in optimizers.items():
    print(f'\tTraining model with {optimizer_name} optimizer...\n')

    for epoch in range(epochs):
      model.train()

      total_loss = 0

      for _, (data, action) in enumerate(train_loader):
        optimizer.zero_grad()

        logits = model(data)


# Delete later:
        print('\t\tLogit shape:', logits.shape, '\n\t\tAction shape:', action.shape, '\n\t\tData shape:', data.shape, '\n')


        loss = loss_function(logits, torch.argmax(action, dim=1))

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

      print(f'\t\tEpoch: {epoch + 1}/{epochs}, Average Loss per Data Point: {(total_loss / len(train_loader)):.4f}')


# Delete later:
      print()


    print('\n\tModel trained. Evaluating model on training data...')

    train_identification_counts, train_correct_counts, train_accuracy = confusion_matrix(model, train_loader)

    print('\tTrain Confusion Matrix:\n')

    for row in train_identification_counts:
      print(f'\t\t{row}')

    print('\n\tTrain Actual Matrix:\n')

    for row in train_correct_counts:
      print(f'\t\t{row}')

    print('\n\tTrain Accuracy:\n\n', f'\t\t{(train_accuracy * 100):.2f}%\n\n', '\tEvaluated model on training data. Evaluating model on validation data...')

    val_identification_counts, val_correct_counts, val_accuracy = confusion_matrix(model, val_loader)

    print('\tValidation Confusion Matrix:\n')

    for row in val_identification_counts:
      print(f'\t\t{row}')

    print('\n\tValidation Actual Matrix:\n')

    for row in val_correct_counts:
      print(f'\t\t{row}')

    print('\n\tValidation Accuracy:\n\n', f'\t\t{(val_accuracy * 100):.2f}%\n\n', '\tEvaluated model on validation data.')

    if val_accuracy > best_val_accuracy or (val_accuracy == best_val_accuracy and train_accuracy > best_train_accuracy):
      best_val_accuracy = val_accuracy
      best_train_accuracy = train_accuracy
      best_model = model.state_dict()
      best_optimizer = optimizer_name
    else:
      print('\tModel did not improve. Skipping to next optimizer.')

  if best_model is not None:
    print(f'\nFound best model with {best_optimizer} optimizer having training accuracy of {train_accuracy * 100}% and validation accuracy of {val_accuracy * 100}%. Testing best model on test data...\n')

    model.load_state_dict(best_model)

    test_identification_counts, test_correct_counts, test_accuracy = confusion_matrix(model, test_loader)

    print('\tTest Confusion Matrix:\n')

    for row in test_identification_counts:
      print(f'\t\t{row}')

    print('\n\tTest Actual Matrix:\n')

    for row in test_correct_counts:
      print(f'\t\t{row}')

    print('\n\tTest Accuracy:\n\n', f'\t\t{(test_accuracy * 100):.2f}%\n')

    return print('Evaluated best model on test data. Done!')
  else:
    return print('No best model found with any optimizer.')

#############################################################################################################################################################################################################
########################################################################################                             ########################################################################################
#######################################################################################                               #######################################################################################
######################################################################################       RUNNING THE PROGRAM       ######################################################################################
#######################################################################################                               #######################################################################################
########################################################################################                             ########################################################################################
#############################################################################################################################################################################################################

if __name__ == "__main__": # If the file is run directly:
  main() # Run the main function.
