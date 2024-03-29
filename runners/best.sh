python main.py --dataset wisconsin --hidden_channels 16 --hops 3 --lr 0.03 --epochs 10000 --dropout 0.4 --wd 0.001 # 89.02,2.8
python main.py --dataset texas --hidden_channels 16 --hops 3 --lr 0.03 --epochs 10000 --dropout 0.4 --wd 0.001  # Report:  89.1891891891892 +- 4.1870090229269366
python main.py --dataset cornell  --hidden_channels 512 --hops 3 --lr 0.03 --epochs 10000 --dropout 0.35 --wd 0.0005 # Report:  85.94594594594595 +- 2.9108998957483796
python main.py --dataset citeseer --hidden_channels 16 --hops 3 --lr 0.03 --epochs 10000 --dropout 0.5 --wd 0.0008 #Report:  77.87176327270667 +- 1.5163752309719407
python main.py --dataset cora --hidden_channels 32 --hops 3 --lr 0.03 --epochs 10000 --dropout 0.5 --wd 0.001 #Report:  88.61167002012073 +- 0.9573744268306076 
python main.py --dataset pubmed --hidden_channels 16 --hops 3 --lr 0.003 --epochs 10000 --dropout 0.5 --wd 0.0005 # Report:  89.78194726166329 +- 0.38502838281395774
python main.py --dataset chamaleon --hidden_channels 16 --hops 3 --lr 0.001 --epochs 10000 --dropout 0.4 --wd 0.0005 # Report:  67.39035087719299 +- 1.1227127838745794
python main.py --dataset squirrel --hidden_channels 256 --hops 3 --lr 0.001 --epochs 10000 --dropout 0.4 --wd 0.0005 # Report:  38.059558117195 +- 1.2706286850172115
python main_large.py --cuda cuda:0 --hops 3 --lr 0.001 --hidden_channels 16 --dropout 0.3 --cuda cuda:0 #Report:  84.75631117980423 +- 0.3457345626646752
python main_large.py --cuda cuda:0 --hops 3 --lr 0.03 --hidden_channels 128 --dropout 0 --cuda cuda:0 --dataset ogbn-arxiv --wd 0.00005 # Report:  63.805272108843546 +- 0.135
python main_large.py --cuda cuda:0 --hops 3 --lr 0.01 --hidden_channels 64 --dropout 0 --cuda cuda:0 --dataset arxiv_year --wd 0.00005 # Report:  48.257275132275126 +- 0.3000402421158805