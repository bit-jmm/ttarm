import numpy as np
import matplotlib.pyplot as plt
import random
from datautil import *

#x = np.linspace(0, 10, 1000)
x = range(7)
for timestep in range(2, 11):
    for metric in ['recall', 'ndcg']:
        for dataset in ['CiteUlike2', 'MovieLens2']:
            bpmf = get_result_at_time('pmf', dataset, metric, timestep=timestep, timeth=5)
            timeSVDpp = get_result_at_time('timeSVD++', dataset, metric, timestep=timestep, timeth=5)
            WALS = get_result_at_time('weighted-als', dataset, metric, timestep=timestep, timeth=5)
            TensorALS = get_result_at_time('tensor-als', dataset, metric, timestep=timestep, timeth=5)
            #BTMF = get_result_at_time('BTMF', dataset, metric, timestep=timestep, timeth=5)
            TRM = get_result_at_time('trm', dataset, metric, timestep=timestep, timeth=5)
            if dataset == 'CiteUlike2':
                TTARM = get_result_at_time('ttarm', dataset, metric, timestep=timestep,
                                           timeth=5)

            plt.figure(figsize=(10, 8))

            plt.plot(x, bpmf, "b*--", label="$BPMF$")
            plt.plot(x, timeSVDpp, "d--", label="$timeSVD++$", color='seagreen')
            plt.plot(x, WALS, "y^--", label="$WALS$")
            plt.plot(x, TensorALS, "kh--", label="$TensorALS$")
        #    plt.plot(x, BTMF, "cp--", label="$BTMF$")
            plt.plot(x, TRM, "rs-", label="$TRM$")
            if dataset == 'CiteUlike2':
                plt.plot(x, TTARM, "m8-", label="$TTARM$")

            #plt.xlabel("Timestep")
            #plt.ylabel("Recall@300")
            plt.xlim(0, 6)
            #plt.ylim(0, 1)
            if metric == 'ndcg' and dataset == 'MovieLens2':
                plt.ylim(0, 0.6)
                plt.yticks(np.arange(0, 0.65, 0.05))
            else:
                plt.ylim(0, 1.1)
                plt.yticks(np.arange(0, 1.1, 0.1))
            plt.xticks([0,1,2,3,4,5,6], [3,10,50,100,300,500,1000])
            #plt.yticks(np.arange(0, 1, 0.1))
            # plt.title("models performance on Recall@300")
            if timestep == 2:
                plt.legend(loc='upper left', numpoints=1)
            filename = metric + '@k' + '_timestep_' + str(timestep) + '_' + dataset +'.png'
            plt.savefig('/Users/jiangming/Dropbox/Research/Latex/papers/TTARM/figures/' + filename)
