# encoding: utf-8
import sys
sys.path.append('/home/zjd/jmm/JPPCF/')

import os
import numpy as np
import util
from JPPCF import *

import logging

argvs = sys.argv

# We fix the num of latent feature
k = 100

lambd = 0.5

eta = 0.2

if len(argvs) == 4:
    k = int(float(argvs[1]))
    lambd = float(argvs[2])
    eta = float(argvs[3])
print 'k: ', k, '\tlambda: ',  lambd, '\teta: ', eta ,'\n'

topic_num = 10

data_path = './data/preprocessed_data/filtered_by_user_doc_like_list_len_10/'

doc_id_map_after_filter = np.loadtxt(\
        './data/preprocessed_data/total_data/doc_id_citeulike_id_map_after_filter.dat.txt', int)
doc_id_map_after_filter_dict = dict(zip(doc_id_map_after_filter[:,0], \
        doc_id_map_after_filter[:,1]))

doc_id_map_in_total = open(\
        './data/preprocessed_data/total_data/doc_id_citeulike_id_map.csv', 'r').\
        readlines()
del doc_id_map_in_total[0]

doc_id_map_in_total_dict = {}
for row in doc_id_map_in_total:
    splits = row.strip().split(',')
    doc_id_map_in_total_dict[int(splits[1])] = int(splits[0])

user_id_map = np.loadtxt(data_path + 'user_id_map.dat.txt', int)
doc_id_map = np.loadtxt(data_path + 'doc_id_map.dat.txt', int)
user_time_dist = np.loadtxt(data_path + 'user_time_distribute.dat.txt', int)
doc_time_dist = np.loadtxt(data_path + 'doc_time_distribute.dat.txt', int)

user_time_dict = dict(zip(user_time_dist[:,0], user_time_dist[:,1]))
doc_time_dict = dict(zip(doc_time_dist[:,0], doc_time_dist[:,1]))

user_id_dict = dict(zip(user_id_map[:,0], user_id_map[:,1]))
ruser_id_dict = dict(zip(user_id_map[:,1], user_id_map[:,0]))
doc_id_dict = dict(zip(doc_id_map[:,0], doc_id_map[:,1]))
rdoc_id_dict = dict(zip(doc_id_map[:,1], doc_id_map[:,0]))

doc_id_citeulike_id_dict = {}
X = np.zeros((doc_id_map.shape[0], 8000))

doc_words = open('./data/preprocessed_data/total_data/mult.dat.txt', 'r').readlines()

# get doc_id citeulike_id dict and doc word matrix
for i in range(doc_id_map.shape[0]):
    citeulike_id = doc_id_map_after_filter_dict[doc_id_map[i, 1]]
    doc_id_citeulike_id_dict[doc_id_map[i, 0]] = citeulike_id

    doc_id_in_total = doc_id_map_in_total_dict[citeulike_id]
    words = doc_words[doc_id_in_total-1].strip().split()
    del words[0]
    for w in words:
        splits = w.split(':')
        X[doc_id_map[i, 0]-1, int(splits[0])] = int(splits[1])

user_num = user_id_map.shape[0]
doc_num = doc_id_map.shape[0]
print 'user_num: ', user_num, '\n'
print 'doc_num: ', doc_num, '\n'

R = np.loadtxt(data_path + 'rating_file.dat.txt', int)
time_step_num = R[:, 2].max()

row = R.shape[0]
for i in range(row):
    user_id = R[i, 0]
    doc_id = R[i, 1]
    R[i, 0] = ruser_id_dict[user_id]
    R[i, 1] = rdoc_id_dict[doc_id]

#exit(0)

regl1nmf = 0.005

regl1jpp = 0.05

epsilon = 1

maxiter = 100

#recall_num = 100

fold_num = 5


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d]\
                            %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='./log/jppcf_with_topic_predict_with_topic_k_' + str(k) + '_lambda_' + \
                            str(lambd) + '_alpha_' + str(regl1jpp) + '_eta_' + str(eta) + '.log',
                    filemode='w')

##################################################################
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，
#并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
##################################################################
#logging.debug('This is debug message')
#logging.info('This is info message')
#logging.warning('This is warning message')


result_dir = './result/tsinghua_server/filter_by_10/jppcf_with_topic/predict_score_with_topic/cross_validate_fold_' + str(fold_num) + \
        '_3models_k_' + str(k) + '_lambda_' + str(lambd) + '_alpha_' + str(regl1jpp) + '_eta_' + str(eta)
recall_result_dir = result_dir + '/recall'
ndcg_result_dir = result_dir + '/ndcg'
ap_result_dir = result_dir + '/ap'

if not os.path.isdir(result_dir):
    os.mkdir(result_dir)
if not os.path.isdir(recall_result_dir):
    os.mkdir(recall_result_dir)
if not os.path.isdir(ndcg_result_dir):
    os.mkdir(ndcg_result_dir)
if not os.path.isdir(ap_result_dir):
    os.mkdir(ap_result_dir)

logging.info('user num: ' + str(user_num) + '\n')
logging.info('doc num: ' + str(doc_num) + '\n')
logging.info('time step num: ' + str(time_step_num) + '\n')

# the start time period used for init of W(1) and H(1), using normal NMF
start = 1
Rt = util.generate_matrice_between_time(R, user_time_dict[start], doc_time_dict[start], start, start)

logging.info('non zero cell num: ' + str(len(np.nonzero(Rt)[0])))
logging.info('start nmf:\n')
(P, Q) = util.nmf(Rt, k, maxiter, regl1nmf, epsilon)

logging.info(str(P.shape) + '\t' + str(Q.shape) + '\n')

# init W and H with nmf
Xt = X[range(doc_time_dict[start]), :]
(W1, H1) = util.nmf(Xt, topic_num, maxiter, regl1nmf, epsilon)

# learning topic distribution by jpp
logging.info('start learning topic distribution by jpp ......')

(W, H, M) = JPPTopic(X, H1, topic_num, lambd, regl1jpp, epsilon, 300, True)

logging.info('end')

# number of period we consider
finT = time_step_num - 1

#for all the consecutive periods
for current_time_step in range(start+1, finT + 1):

    logging.info('\n=========================\n')
    logging.info('time_step number %i:\t' + str(current_time_step))
    logging.info('----------------\n')

    Po = P

    jrecall_dict = {}

    jndcg_dict = {}

    jap_dict = {}

    current_user_num = user_time_dict[current_time_step]
    current_doc_num = doc_time_dict[current_time_step]

    current_user_like_dict = {}
    like_file = open(data_path + 'user_like_list_at_time_step' + str(current_time_step) + '.dat.txt')
    for user in like_file.readlines():
        splits = user.split()
        like_list = []
        for i in range(2, len(splits)):
            like_list.append(rdoc_id_dict[int(splits[i])])
        current_user_like_dict[ruser_id_dict[int(splits[0])]] = like_list

    for fold_id in range(fold_num):
    #for fold_id in [0]:
        train_data_path = data_path + 'time_step_' + str(current_time_step) + \
                '/data_' + str(fold_id) + '/train.dat.txt'
        current_data_path = data_path + 'time_step_' + \
                            str(current_time_step) + '/data_' + \
                            str(fold_id)
        Rt = util.generate_matrice_for_file2(train_data_path,
                                             current_user_num,
                                             current_doc_num,
                                             ruser_id_dict,
                                             rdoc_id_dict
                                             )

        logging.info('non zero cell num: ' + str(len(np.nonzero(Rt)[0])))

        # calculate user item topic similarity matrix
        Ct = util.cal_topic_similarity_matrix(W,
                                              current_data_path,
                                              current_user_num,
                                              current_doc_num,
                                              ruser_id_dict,
                                              rdoc_id_dict,
                                              current_user_like_dict,
                                              doc_time_dict[1])

        logging.info('computing JPP_with_topic decomposition...')

        Po = util.reshape_matrix(Po, current_user_num, k)

        P, Q, S = JPPCF_with_topic(Rt, Po, Ct, k, eta, lambd, regl1jpp,  epsilon, maxiter, True)
        PredictR = ((1-eta)*np.dot(P, Q)) + (eta*Ct)
        NormPR = PredictR / PredictR.max()

        logging.info('[ok]\n')

        logging.info('\t fold_id:' + str(fold_id) + '\n')
        for recall_num in [3,5,10,50,100,150,200,250,300]:
            logging.info('\trecall at ' + str(recall_num) + ':')
            jppcf_recall = util.performance_cross_validate_recall2(
                    NormPR, current_data_path, recall_num,
                    ruser_id_dict, rdoc_id_dict, current_user_like_dict)


            if jrecall_dict.has_key(recall_num):
                    jrecall_dict[recall_num].append(jppcf_recall)
            else:
                    jrecall_dict[recall_num] = [jppcf_recall]
            logging.info('\t\tJPPCF_with_topic :  ' + str(jppcf_recall) + '\n\n\n')

            # ndcg performance
            logging.info('\nndcg at ' + str(recall_num) + ':')
            jppcf_ndcg = util.performance_ndcg(
                    NormPR, current_data_path, recall_num,
                    ruser_id_dict, rdoc_id_dict, current_user_like_dict)


            if jndcg_dict.has_key(recall_num):
                    jndcg_dict[recall_num].append(jppcf_ndcg)
            else:
                    jndcg_dict[recall_num] = [jppcf_ndcg]
            logging.info('\t\tJPPCF_with_topic :  ' + str(jppcf_ndcg) + '\n\n\n')

            # ap performance
            logging.info('\nap at ' + str(recall_num) + ':')
            jppcf_ap = util.performance_ap(
                    NormPR, current_data_path, recall_num,
                    ruser_id_dict, rdoc_id_dict, current_user_like_dict)

            if jap_dict.has_key(recall_num):
                    jap_dict[recall_num].append(jppcf_ap)
            else:
                    jap_dict[recall_num] = [jppcf_ap]
            logging.info('\t\tJPPCF_with_topic :  ' + str(jppcf_ap) + '\n\n')

    logging.info('current_time_step: ' + str(current_time_step) + '\n')

    for recall_num in [3,5,10,50,100,150,200,250,300]:
        # recall
        logging.info('\trecall at ' + str(recall_num) + ':')
        avg_jppcf_recall = util.avg_of_list(jrecall_dict[recall_num])
        logging.info('\t\tavg jppcf_with_topic :  ' + str(avg_jppcf_recall) + '\n\n\n')

        exist = False
        if os.path.isfile(recall_result_dir + '/recall_at_' + str(recall_num)  + '.txt'):
            exist = True

        result_file = open(recall_result_dir + '/recall_at_' + str(recall_num)  + '.txt', 'a')
        if not exist:
            result_file.write('jppcf_with_topic\n')

        result_file.write(str(avg_jppcf_recall) + '\n')
        result_file.close()

        # ndcg
        logging.info('\tndcg at ' + str(recall_num) + ':')
        avg_jppcf_ndcg = util.avg_of_list(jndcg_dict[recall_num])
        logging.info('\t\tavg jppcf_with_topic :  ' + str(avg_jppcf_ndcg) + '\n\n\n')

        exist = False
        if os.path.isfile(ndcg_result_dir + '/ndcg_at_' + str(recall_num)  + '.txt'):
            exist = True

        result_file = open(ndcg_result_dir + '/ndcg_at_' + str(recall_num)  + '.txt', 'a')
        if not exist:
            result_file.write('jppcf_with_topic\n')

        result_file.write(str(avg_jppcf_ndcg) + '\n')
        result_file.close()

        # ap
        logging.info('\tap at ' + str(recall_num) + ':')
        avg_jppcf_ap = util.avg_of_list(jap_dict[recall_num])
        logging.info('\t\tavg jppcf_with_topic :  ' + str(avg_jppcf_ap) + '\n\n\n')

        exist = False
        if os.path.isfile(ap_result_dir + '/ap_at_' + str(recall_num)  + '.txt'):
            exist = True

        result_file = open(ap_result_dir + '/ap_at_' + str(recall_num)  + '.txt', 'a')
        if not exist:
            result_file.write('jppcf_with_topic\n')

        result_file.write(str(avg_jppcf_ap) + '\n')
        result_file.close()

    logging.info('=========================\n')

logging.info('\n all process done! exit now...')
