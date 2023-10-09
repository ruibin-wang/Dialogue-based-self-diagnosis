import json
import math
from pathlib import Path
from typing import Dict
from collections import Counter, OrderedDict



def extract_symptoms(text:str):
    symptoms = text.split(",")
    symptoms_set = [i.lstrip() for i in symptoms]
    return symptoms_set

def overlap_count_and_remove(list1, list2):
    # 转化为集合以找到重叠的元素
    set1 = set(list1)
    set2 = set(list2)

    # 找到重叠的元素
    overlaps = set1.intersection(set2)

    # 从原列表中删除这些重叠的元素
    # list1[:] = [x for x in list1 if x not in overlaps]
    # list2[:] = [x for x in list2 if x not in overlaps]

    # 返回重叠元素的数量
    return len(overlaps)


def disease_score_sorted(known_symptoms, related_disease, nomal_dis_symp_sort):
    disease_score_set = []
    for dis in related_disease:
        overlap_count = overlap_count_and_remove(known_symptoms, nomal_dis_symp_sort[dis])

        # # sort again, for symptoms in disease
        # temp_set = [(i, s_sort[i]) for i in dis_list]
        # symp_list = sorted(temp_set, key=lambda x:x[1], reverse=True)
        # nomal_dis_symp_sort[dis] = [i[0] for i in symp_list]

        disease_score_set.append((dis, overlap_count/len(nomal_dis_symp_sort[dis]), overlap_count, len(nomal_dis_symp_sort[dis])))

    disease_score_set_sort = sorted(disease_score_set, key=lambda x:x[1], reverse=True)

    return disease_score_set_sort


def s_sort_update(s_sort:dict, known_symptoms:list):
    for symp in known_symptoms:
        if symp in s_sort.keys():
            del s_sort[symp]

    update_symp_sort = dict(sorted(s_sort.items(), key=lambda x: x[1], reverse=True))
    return update_symp_sort


def index_dict(s_sort:dict):
    index_s_sort = list(OrderedDict(s_sort).items())
    return index_s_sort

def find_first_not_in(a, b):
    for item in b:
        if item not in a:
            return item
    return None


def turn0_processing(user_resp, known_symptoms, nomal_dis_symp_sort):
    related_disease = []
    extract_symp = extract_symptoms(user_resp)
    known_symptoms += extract_symp

    ## the disease related to the symptom

    for symp in known_symptoms:
        for key in nomal_dis_symp_sort.keys():
            if symp in nomal_dis_symp_sort[key]:
                related_disease.append(key)

    related_disease = list(dict.fromkeys(related_disease).keys())

    disease_score_set_sort = disease_score_sorted(known_symptoms, related_disease, nomal_dis_symp_sort)

    return known_symptoms, related_disease, disease_score_set_sort


##########################


def main(N, s_sort, nomal_dis_symp_sort):


    abandon_symptoms = []
    known_symptoms = []
    for turn in range(0, N):
        if turn == 0:
            print("System: What can I do for you? Please give a description of your situation.")
            user_input = input("Response:")

            user_input = user_input.lower()

            known_symptoms, related_disease, disease_score_set_sort = turn0_processing(user_input, known_symptoms, nomal_dis_symp_sort)

        else:

            s1 = find_first_not_in(known_symptoms, nomal_dis_symp_sort[disease_score_set_sort[0][0]])

            s_sort = s_sort_update(s_sort, [s1])

            index_s_sort = index_dict(s_sort.copy())
            s2 = index_s_sort[0][0]

            print("System: Do you have " + str(s1) + " or " + str(s2) +" ?")

            user_input = input("Response:")

            if "both" in user_input:
                known_symptoms += [s1, s2]

            elif "first" in user_input:
                known_symptoms += [s1]
                abandon_symptoms.append(s2)

            elif "last" in user_input:
                known_symptoms += [s2]
                abandon_symptoms.append(s1)

            elif "none" in user_input:
                abandon_symptoms += [s1, s2]

            s_sort = s_sort_update(s_sort, [s2])
            disease_score_set_sort = disease_score_sorted(known_symptoms, related_disease, nomal_dis_symp_sort)

            if turn == N-1 or disease_score_set_sort[0][1]==1.0:
                print("You might have \n" + str(disease_score_set_sort[0][0]) + " with a possibility of " + str(disease_score_set_sort[0][1]) + "\n" +
                      str(disease_score_set_sort[1][0]) + " with a possibility of " + str(disease_score_set_sort[1][1]) + ".")



if __name__ =="__main__":
    N = 4
    test_str = "Hello. I'm in a lot of pain - I've got a headache, a high temperature, and my face is swollen."
    # symptom_path = root_result_dir/"watson_analyze/oneliners-name-code.json"
    symptom_path = "D://Code//IntelPA-main//intelPA/graph/SymptomDiseaseInd_normalized_name.json"
    with open(symptom_path, 'r') as load_f:
        original_load_dict = json.load(load_f)


    load_dict = {}
    for key in original_load_dict.keys():
        if len(original_load_dict[key]) > 5:
            load_dict[key] = original_load_dict[key]


    ###################################################
    ## 计算s_sort
    all_symp = []
    normal_dis_symp = {}
    for key in load_dict.keys():
        temp = []
        temp = [i[1] for i in load_dict[key]]

        ### temp contains symptoms, sort the symptom through the number of the symptoms

        normal_dis_symp[key] = temp
        all_symp += temp

    counter_symp = dict(Counter(all_symp))  ## sort the number of symptoms
    s_sort = dict(sorted(counter_symp.items(), key=lambda x: x[1], reverse=True))

    nomal_dis_symp_sort = {}
    for key in normal_dis_symp.keys():
        temp_list = [(i, s_sort[i]) for i in normal_dis_symp[key]]
        symp_list = sorted(temp_list, key=lambda x: x[1], reverse=True)
        nomal_dis_symp_sort[key] = [i[0] for i in symp_list]


    main(N, s_sort, nomal_dis_symp_sort)



























































