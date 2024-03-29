import argparse
import os
import torch
import numpy as np
import pandas as pd
import time
from torch_geometric.datasets import Planetoid,WebKB,Actor,WikipediaNetwork, LINKXDataset
from torch_geometric.nn.models import MLP
from torch_geometric.transforms import *
import torch_geometric.transforms as T
from models import *
from utils import *
import warnings
warnings.filterwarnings("ignore")
################### Arguments parameters ###################################
parser = argparse.ArgumentParser()
parser.add_argument(
    "--dataset",
    default="wisconsin",
    choices=["texas","wisconsin","actor","cornell","squirrel","chamaleon","cora","citeseer","pubmed","penn94"],
    help="You can choose between texas, wisconsin, actor, cornell, squirrel, chamaleon, cora, citeseer, pubmed",
)
parser.add_argument(
    "--cuda",
    default="cuda:0",
    choices=["cuda:0","cuda:1","cpu"],
    help="You can choose between cuda:0, cuda:1, cpu",
)
parser.add_argument(
        "--hidden_channels", type=int, default=64, help="Hidden channels for the unsupervised model"
)
parser.add_argument(
        "--dropout", type=float, default=0.35, help="Dropout rate"
    )
parser.add_argument(
        "--lr", type=float, default=0.01, help="Outer learning rate of model"
    )
parser.add_argument(
        "--wd", type=float, default=5e-4, help="Outer weight decay rate of model"
    )
parser.add_argument(
        "--epochs", type=int, default=1000, help="Epochs for the model"
    )
parser.add_argument(
        "--hops", type=int, default=2, help="Number of centers"
)
args = parser.parse_args()
args.cuda = 'cpu' if not torch.cuda.is_available() else 'cuda:0'
################### Importing the dataset ###################################
if args.dataset in ["wisconsin","cornell","texas"]:
    transform = T.Compose([T.NormalizeFeatures(), T.ToUndirected()])
    dataset = WebKB(root='./data',name=args.dataset,transform=transform)
    data = dataset[0]
elif args.dataset == "actor":
    transform = T.Compose([T.NormalizeFeatures(), T.ToUndirected()])
    dataset  = Actor(root='./data', transform=transform)
    dataset.name = "film"
    data = dataset[0]
elif args.dataset in ["squirrel","chamaleon"]:
    transform = T.Compose([T.ToUndirected()])
    dataset = WikipediaNetwork(root='./data',name=args.dataset,transform=transform)
    data = dataset[0]    
elif args.dataset in ["pubmed","cora","citeseer"]:
    transform = T.Compose([T.ToUndirected()])
    dataset = Planetoid(root='./data',name=args.dataset)
    data = dataset[0]
init_edge_index = data.edge_index.clone()
hops = khop_graphs_sparse(data.x,
                          data.edge_index,
                            args.hops,
                            args.dataset,
                            args.cuda)
hops.append(init_edge_index)
print("Done!")
data.edge_index = hops
print()
print(f'Dataset: {dataset}:')
print('======================')
print(f'Number of graphs: {len(dataset)}')
print(f'Number of features: {dataset.num_features}')
print(f'Number of classes: {dataset.num_classes}')
print()
print(data) 
print('===========================================================================================================')
################### CUDA ###################################
device = torch.device(args.cuda)
data = data.to(device)   
print("Device: ",device)
################### Training the model in a supervised way ###################################
results = []
for i in range(10):
    # Time per split
    start = time.time()
    with open('splits/'+dataset.name+'_split_0.6_0.2_'+str(i)+'.npz', 'rb') as f:
                splits = np.load(f)
                train_mask = torch.tensor(splits['train_mask']).to(device)
                val_mask = torch.tensor(splits['val_mask']).to(device)
                test_mask = torch.tensor(splits['test_mask']).to(device)        
    print('===========================================================================================================')
    print('Split: ',i)
    print('===========================================================================================================')
    if args.dataset in ["chamaleon","squirrel","actor"]:
        model = MO_GNN_large_xl(in_channels=data.x.shape[1],
                        hidden_channels=args.hidden_channels,
                        out_channels=data.y.max().item()+1,
                        num_layers=args.hops,
                        dropout=args.dropout,seed=i).to(device)
    else:
        model = MO_GNN_large(in_channels=data.x.shape[1],
                    hidden_channels=args.hidden_channels,
                    out_channels=data.y.max().item()+1,
                    num_layers=args.hops,
                    dropout=args.dropout,seed=i).to(device)
    criterion = torch.nn.NLLLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.wd)
    test_acc = 0
    patience = 0
    for epoch in range(args.epochs):
        loss,acc_train = train(data,model,train_mask,optimizer,criterion)
        acc_val = test(data,model,val_mask)
        acc_test = test(data,model,test_mask)
        print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}, Train Acc: {acc_train:.4f}, Val Acc: {acc_val:.4f}, Test Acc: {acc_test:.4f}')
        if acc_test > test_acc:
            test_acc = acc_test
        if test_acc > acc_test:
            patience += 1
        else:
            patience = 0
        if patience == 500:
            break
    end = time.time()
    del model
    del optimizer
    del criterion
    print('===========================================================================================================')
    print('Test Accuracy: ',test_acc,'Time: ',end-start)
    print('===========================================================================================================')
    results.append(test_acc)
print('===========================================================================================================')
print('Report: ',np.mean(results)*100,'+-',np.std(results)*100)
print('===========================================================================================================')
print(' Configuration: ',args)
print('===========================================================================================================')

# Now we check if it is created a csv with the configuration and the results
if os.path.isfile('results.csv'):
    # If the file exists, then we append the configuration and the results
    # The columns are: dataset, model, hidden_channels, lr, epochs, num_centers, AUC, AP
    res = pd.read_csv('results.csv')
    # Check if the configuration is already in the csv
    if res[(res['dataset'] == args.dataset) & (res['hidden_channels'] == args.hidden_channels) & (res['lr'] == args.lr) & (res['epochs'] == args.epochs) & (res['hops'] == args.hops) & (res['wd'] == args.wd) & (res['dropout'] == args.dropout)].shape[0] == 0:
        # If the configuration is not in the csv, then we append it
        #res = res.append({'dataset': args.dataset, 'hidden_channels': args.hidden_channels, 'lr': args.lr, 'dropout': args.dropout, 'epochs': args.epochs, 'hops': args.hops, 'n_layers': args.n_layers, 'Accuracy': np.round(np.mean(np.array(results))*100,2), 'std': np.round(np.std(np.array(results))*100,2)}, ignore_index=True)
        res = pd.concat([res, pd.DataFrame({'dataset': args.dataset, 'hidden_channels': args.hidden_channels, 'lr': args.lr, 'dropout': args.dropout, 'epochs': args.epochs, 'hops': args.hops, 'wd': args.wd, 'Accuracy': np.round(np.mean(np.array(results))*100,2), 'std': np.round(np.std(np.array(results))*100,2)}, index=[0])], ignore_index=True)
        res.to_csv('results.csv', index=False)
    res.to_csv('results.csv', index=False)
else:
    # If the file does not exist, then we create it and append the configuration and the results
    res = pd.DataFrame(columns=['dataset', 'hidden_channels', 'lr','dropout', 'epochs', 'hops', 'wd', 'Accuracy', 'std'])
    #res = res.append({'dataset': args.dataset, 'hidden_channels': args.hidden_channels, 'lr': args.lr, 'dropout': args.dropout, 'epochs': args.epochs, 'hops': args.hops, 'n_layers': args.n_layers, 'Accuracy': np.round(np.mean(np.array(results))*100,2), 'std': np.round(np.std(np.array(results))*100,2)}, ignore_index=True)
    res = pd.concat([res, pd.DataFrame({'dataset': args.dataset, 'hidden_channels': args.hidden_channels, 'lr': args.lr, 'dropout': args.dropout, 'epochs': args.epochs, 'hops': args.hops, 'wd': args.wd, 'Accuracy': np.round(np.mean(np.array(results))*100,2), 'std': np.round(np.std(np.array(results))*100,2)}, index=[0])], ignore_index=True)
    res.to_csv('results.csv', index=False)
