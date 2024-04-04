# -*- coding: utf-8 -*-
"""M23CSA009_DLOps_ClassAssignment_2_Q_2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UB2-dfYir0WeA3jVboVqXNNIkLs5W4GC

## Roll No. M23CSA009
### Last digit of roll no. = 9; 9 mod 3 = 0
### dataset used : STL10
### Optimizers chosen : Adam, Adagrad, RMSProp
"""

#required libraries
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#preprocessing datasets and make the dataloader
#renets take 224*224 images as input so we need to resize the images
transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

train_dataset = datasets.STL10(root='./data', split='train', download=True, transform=transform)
test_dataset = datasets.STL10(root='./data', split='test', download=True, transform=transform)

batch_size = 64
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

#define the model:
model = models.resnet50(pretrained=True)
features = model.fc.in_features
#modify the fully connected layer for the new task
model.fc = nn.Linear(features, 10)  #STL10 has 10 classes
model = model.to(device)
optimizers = {
    'Adam': optim.Adam(model.parameters(), lr=0.001),
    'Adagrad': optim.Adagrad(model.parameters(), lr=0.001),
    'RMSprop': optim.RMSprop(model.parameters(), lr=0.001)
}

criterion = nn.CrossEntropyLoss()

#training the model for 5 epochs only as the training is taking a lot of time for 1 epoch
def train_model(optimizer, model, criterion, train_loader, epochs=5):
    model.train()
    train_losses = []
    train_accuracies = []

    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # Statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        # Calculate training loss and accuracy
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = correct / total

        train_losses.append(epoch_loss)
        train_accuracies.append(epoch_acc)

        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}, Accuracy: {epoch_acc:.4f}")

    return train_losses, train_accuracies

results = {}
for optimizer_name, optimizer in optimizers.items():
    print(f"Optimizer : {optimizer_name}")
    train_losses, train_accuracies = train_model(optimizer, model, criterion, train_loader, epochs=5)
    results[optimizer_name] = (train_losses, train_accuracies)

#plots for the training losses
plt.figure(figsize=(10, 5))
for optimizer_name, (train_losses, train_accs) in results.items():
    plt.plot(train_losses, label=f'Loss for : {optimizer_name}')
plt.xlabel('Epoch')
plt.ylabel('Training Loss')
plt.title('Comparison of Training loss curves for 3 optimizers')
plt.legend()
plt.show()

#plots for teh accuracies
plt.figure(figsize=(10, 5))
for optimizer_name, (train_losses, train_accs) in results.items():
    plt.plot(train_accs, label=f'{optimizer_name} Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Training Accuracy')
plt.title('Comparison of Training accuracy curves for 3 optimizers')
plt.legend()
plt.show()

from sklearn.metrics import top_k_accuracy_score

def calculate_topk_accuracy(model, test_loader, k):
    y_true = []
    y_pred_probs = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            probabilities = torch.softmax(outputs, dim=1)
            y_pred_probs.extend(probabilities.cpu().numpy())
            y_true.extend(labels.cpu().numpy())

    topk_accuracy = top_k_accuracy_score(y_true, y_pred_probs, k=k)
    return topk_accuracy

# Calculate top-1 and top-5 accuracy
top1_accuracy = calculate_topk_accuracy(model, test_loader, k=1)
top5_accuracy = calculate_topk_accuracy(model, test_loader, k=5)

print(f"Top-1 Accuracy: {top1_accuracy:.4f}")
print(f"Top-5 Accuracy: {top5_accuracy:.4f}")