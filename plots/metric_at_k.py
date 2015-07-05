import numpy as np
import matplotlib.pyplot as plt
import random
from datautil import *

#x = np.linspace(0, 10, 1000)
x = range(2, 11)

for metric in ['recall', 'ndcg']:
    for topk in [50, 100, 300, 500]:
        for dataset in ['CiteUlike2', 'MovieLens2']:
            bpmf = get_avg_result('pmf', dataset, metric, topk=topk, timeth=5)
            timeSVDpp = get_avg_result('timeSVD++', dataset, metric, topk=topk, timeth=5)
            WALS = get_avg_result('weighted-als', dataset, metric, topk=topk, timeth=5)
            TensorALS = get_avg_result('tensor-als', dataset, metric, topk=topk, timeth=5)
            BTMF = get_avg_result('BTMF', dataset, metric, topk=topk, timeth=3)
            TRM = get_avg_result('trm', dataset, metric, topk=topk, timeth=5)
            if dataset == 'CiteUlike2':
                TTARM = get_avg_result('ttarm', dataset, metric, topk=topk, timeth=5)

            plt.figure(figsize=(10, 8))

            plt.plot(x, bpmf, "b*--", label="$BPMF$")
            plt.plot(x, timeSVDpp, "d--", label="$timeSVD++$", color='seagreen')
            plt.plot(x, WALS, "^-.", label="$WALS$", color='purple')
            plt.plot(x, TensorALS, "kh:", label="$TensorALS$")
            plt.plot(x, BTMF, "p--", label="$BTMF$", color='gold')
            plt.plot(x, TRM, "rs-", label="$TRM$")
            if dataset == 'CiteUlike2':
                plt.plot(x, TTARM, "m8-", label="$TTARM$")
            plt.xlabel("Timestep t")
            if metric == 'recall':
                plt.ylabel("Recall@"+str(topk))
            else:
                plt.ylabel("NDCG@"+str(topk))
            plt.xlim(2, 10)
            if metric == 'ndcg' and dataset == 'MovieLens2':
                plt.ylim(0, 0.5)
            if metric == 'ndcg' and dataset == 'MovieLens2':
                plt.yticks(np.arange(0, 0.55, 0.05))
            else:
                plt.yticks(np.arange(0, 1.1, 0.1))
            # plt.title("models performance on Recall@300")

            if metric == 'recall' and dataset == 'MovieLens2':
                plt.legend(loc='upper left', numpoints=1)
            #plt.show()
            filename = metric + '@' + str(topk) + '_' + dataset +'.png'
            plt.savefig('/Users/jiangming/Dropbox/Research/Latex/papers/TTARM/figures/' + filename)