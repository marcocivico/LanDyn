# -*- coding: utf-8 -*-

import pandas as pd 
import numpy as np 
from collections import Counter 
import random 
import time 
 
# -- Parameters -- 
p_learning = 0 
learning_rate = 1 
np.random.seed(24) 
random.seed(24) 

# ---------- Data ---------- 
# Read agent_data 
filepath=r"/Users/civico/Desktop/Tentativi/SoloIE/correct_database_soloIE.xlsx"
print('Importing agent data...') 
agent_data = pd.read_excel(filepath, sheet_name="Database")
 
agent_data['lvl1'] = agent_data['lvl1'].astype('int32') 
agent_data['lvl2'] = agent_data['lvl2'].astype('int32') 
agent_data['lvl3'] = agent_data['lvl3'].astype('int32') 
 
# Ratios 
print('Importing population ratios...') 
ratios = pd.read_excel(filepath, sheet_name="Agents") 
ratios_dict = pd.Series(ratios["No croatia.2"].values, index=ratios["Country"]).to_dict() 
 
# Language PROXIMITY matrix. 
matrix_data = pd.read_excel(filepath, sheet_name="Dyen") 
SimMat = matrix_data.to_numpy()[:,1:]
simMatLanguages = matrix_data.columns[1:]
 
# Hash tables (for accessing SimMat elements) 
langIdx = {} 
idxLang = {} 
for idx, lang in enumerate(simMatLanguages): 
    langIdx[lang] = idx 
    idxLang[idx] = lang 
 
# ------- Print formatting ------- 
pd.set_option('display.max_rows', 500) 
pd.set_option('display.max_columns', 500) 
pd.set_option('display.width', 1000) 
# ------------------------------- 

class Agent: 
    def __init__(self, data): 
        self.residence = data[0] 
        self.ol1 = data[1] 
        self.ol2 = data[2] 
        self.ol3 = data[3] 
        self.nationality1 = data[4] 
        self.nationality2 = data[5] 
        self.nationality3 = data[6] 
 
        self.mt1 = data[7] 
        self.mt2 = data[8] 
        self.mt3 = data[9] 
        self.mt4 = data[10] 
 
        self.fl1 = data[11] 
        self.lvl1 = data[12] 
 
        self.fl2 = data[13] 
        self.lvl2 = data[14] 
 
        self.fl3 = data[15] 
        self.lvl3 = data[16] 
 
        self.attitude = data[17] 
        self.edu = data[18] 
        self.edugroup = data[19] 
        self.sex = data[20] 
        self.age = data[21] 
        self.agegroup1 = data[22] 
        self.agegroup2 = data[23] 
        self.profession = data[24] 
        self.living = data[25] 
 
        # ----------------------------------------------------------------------- 
        self.all_mts = [lang for lang in [self.mt1, self.mt2, self.mt3, self.mt4] if lang != 'NN'] 
        self.all_fls = [lang for lang in [data[11], data[13], data[15]] if lang != 'NN']
        self.all_fl_lvls_list = [lang for lang in [data[12], data[14], data[16]] if lang != 0]
        self.fl_lvl_dict = dict(zip(self.all_fls, self.all_fl_lvls_list)) 
        self.currently_learning = 0 
        self.mts_and_flAtLvl3 = self.all_mts + [lang for lang in self.all_fls if self.fl_lvl_dict[lang] == 3] 
 
    def fl_closest_to_lvl3(self): 
        all_fl_lvls = np.array([lang for lang in self.all_fl_lvls_list], dtype=np.float) 
        all_below_lvl3 = np.where(all_fl_lvls < 3)[0] 
        closest_to_lvl3 = all_below_lvl3[all_fl_lvls[all_below_lvl3].argmax()] 
        return closest_to_lvl3 
 
    def reset_lang_learning_method(self): 
        self.language_learning_method_selected = 0 
 
    def fl_at_lvl3(self): 
        fl_at_lvl3_list = [] 
        for fl in self.fl_lvl_dict.keys(): 
            if self.fl_lvl_dict[fl] == 3: 
                fl_at_lvl3_list.append(fl) 
        return fl_at_lvl3_list 
 
    def check_all_fl_lvl3(self): 
        if (len(self.all_fl_lvls_list) == 3) and (all(i==3 for i in self.all_fl_lvls_list)): 
            return int(1) 
        else: 
            return int(0) 
 
    def  has_fl(self): 
        return any(i<3 for i in self.all_fl_lvls_list) 
 
    def highest_fl_lvl(self): 
        all_fls_and_lvls = list(zip(self.all_fls, self.all_fl_lvls_list)) 
        highest_fl = max(all_fls_and_lvls, key=lambda x: x[1]) 
        return highest_fl 
 
    def empty_fl_slot(self): 
        for idx, lang in enumerate(self.all_fls, 1): 
            if self.fl_lvl_dict[lang] == None: 
                return idx 
            else: 
                continue 
 
    def at_least_1FL_below3(self): 
        return any(i<3 for i in self.all_fl_lvls_list) 
 
class Agent_repository: 
    def __init__(self): 
        self.all_agents = [] 
 
    def populate_repository(self): 
        global agent_data, ratios_dict 
 
        # random sampling based on ratios 
        for country in ratios_dict.keys(): 
            agent_data_temp = agent_data[agent_data['residence'] == country] 
            agent_data_temp.reset_index(drop=True, inplace=True) 
            for i in range(ratios_dict[country]): 
                random_agent_index = np.random.choice(np.arange(len(agent_data_temp)), 1)[0] 
                agent = Agent(agent_data_temp.iloc[[random_agent_index]].values.tolist()[0]) 
                self.all_agents.append(agent) 
 
    def continue_or_coinFlip(self): 
        global p_learning 
        for idx, agent in enumerate(self.all_agents): 
 
            if agent.check_all_fl_lvl3 == int(1):
                agent.currently_learning = 0 
                continue 
            else: 
                if agent.at_least_1FL_below3() is True:
                    agent.currently_learning = 1 
                else: 
                    coin_flip = np.random.uniform(0, 1, 1)[0] 
                    if coin_flip > p_learning: 
                        agent.currently_learning = 1 
                    else: 
                        continue 
 
    def update_agents(self, pick_lang_rule): 
        global learning_rate 
        all_agents_len = len(self.all_agents) 
 
        most_freq_languages = [i[0] for i in self.max_count_lang(top_n=6)] 
        for idx, agent in enumerate(self.all_agents): 
            if agent.check_all_fl_lvl3 == 1:
                agent.currently_learning = 0 
                continue 
            else: 
                if agent.currently_learning == 1:
 
                    if agent.at_least_1FL_below3() == True:
                        closest_to_lvl3_idx = agent.fl_closest_to_lvl3() 
                        actual_lang = agent.all_fls[closest_to_lvl3_idx] 
                        max_sim = [SimMat[langIdx[lang], langIdx[actual_lang]] for lang in agent.mts_and_flAtLvl3] 
                        max_sim = max(max_sim) 
                        updated_language_score = min(agent.all_fl_lvls_list[closest_to_lvl3_idx] + float(max_sim) * learning_rate, 3)
                        agent.all_fl_lvls_list[closest_to_lvl3_idx] = updated_language_score 
                        if  updated_language_score == 3:
                          agent.mts_and_flAtLvl3.append(actual_lang)
                    else: 
                        if pick_lang_rule == 1: 
                            self.pick_language_rule_1(agent, frequency_list=most_freq_languages) 
                        elif pick_lang_rule == 2: 
                            self.pick_language_rule_2(agent) 
                        elif pick_lang_rule == 3: 
                            self.pick_language_rule_3(agent, frequency_list=most_freq_languages) 
 
 
    def max_count_lang(self, top_n=6): 
        all_relevent_langs = [] 
        for agent in self.all_agents: 
            all_relevent_langs += agent.all_mts 
            for fl in agent.fl_at_lvl3(): 
                all_relevent_langs.append(fl) 
        most_common = [i for i in Counter(all_relevent_langs).most_common(n=top_n)]  # list of tuples 
        return most_common

    def pick_language_rule_1(self, agent, frequency_list): 
        global SimMat, langIdx 
        agent_langs = agent.all_mts + agent.all_fls 
        selected_most_freq_lang = 0 
        most_freq_languages = frequency_list 
        for most_freq_lang in most_freq_languages: 
            if most_freq_lang not in agent_langs: 
                selected_most_freq_lang = most_freq_lang
                break
            else: 
                continue 
 
        max_sim = [SimMat[langIdx[lang], langIdx[selected_most_freq_lang]] for lang in agent.mts_and_flAtLvl3] # index 24 is out of bounds for axis zero for size 24 
        max_sim = max(max_sim) 
 
        agent.all_fl_lvls_list.append(min(max_sim * learning_rate, 3)) 
        agent.all_fls.append(selected_most_freq_lang) 
 
    def pick_language_rule_2(self, agent): 
        global SimMat, langIdx, idxLang, simMatLanguages 
        similar_langs = [] 
        for lang in agent.mts_and_flAtLvl3: 
            for sim_lang in simMatLanguages: 
                if sim_lang not in agent.mts_and_flAtLvl3: 
                    similarity = SimMat[langIdx[lang], langIdx[sim_lang]] 
                    similar_langs.append((sim_lang, similarity))
        similar_langs = sorted(similar_langs, key=lambda x: x[1])[::-1]
        most_similar_lang = similar_langs[0][0] 
        most_similar_lang_sim = similar_langs[0][1] 
        agent.all_fls.append(most_similar_lang) 
        agent.all_fl_lvls_list.append(min(most_similar_lang_sim * learning_rate, 3)) 

    def pick_language_rule_3(self, agent, frequency_list): 
        global SimMat, langIdx, idxLang, simMatLanguages 
        most_freq_langs = frequency_list
        #print(most_freq_langs)
        #time.sleep(100)
        similar_langs = [] 
        for lang in agent.mts_and_flAtLvl3: 
            for sim_lang in simMatLanguages: 
                if (sim_lang not in agent.mts_and_flAtLvl3) and (sim_lang in most_freq_langs): 
                    similarity = SimMat[langIdx[lang], langIdx[sim_lang]] 
                    similar_langs.append((sim_lang, similarity)) 
        similar_langs = sorted(similar_langs, key=lambda x: x[1])[::-1] 
        most_similar_lang = similar_langs[0][0] 
        most_similar_lang_sim = similar_langs[0][1]
        agent.all_fls.append(most_similar_lang) 
        agent.all_fl_lvls_list.append(min(most_similar_lang_sim * learning_rate, 3)) 
 
print('Build agent repository') 
Agent_repo = Agent_repository()
 
print('Populate the repository.') 
Agent_repo.populate_repository()
 
for iteration in range(6): 
    print(iteration) 
    start_time = time.time() 
    print('Continue learning or flip coin.') 
    Agent_repo.continue_or_coinFlip()
    print('Update agents...') 
    Agent_repo.update_agents(pick_lang_rule=3)
    print('Elapsed time: {} sec'.format(time.time() - start_time))
 
final_data = [] 
final_data_fl_lvls = [] 
for agent in Agent_repo.all_agents: 
    temp_agent_results = [agent.residence, 
                          agent.ol1, 
                          agent.ol2, 
                          agent.ol3, 
                          agent.nationality1, 
                          agent.nationality2, 
                          agent.nationality3, 
                          agent.attitude, 
                          agent.edu, 
                          agent.edugroup, 
                          agent.sex, 
                          agent.age, 
                          agent.agegroup1, 
                          agent.agegroup2, 
                          agent.profession, 
                          agent.living, 
                          agent.mt1, 
                          agent.mt2, 
                          agent.mt3, 
                          agent.mt4] 
 
    for fl in agent.all_fls: 
        temp_agent_results.append(fl) 
 
    final_data_fl_lvls.append(agent.all_fl_lvls_list) 
 
    final_data.append(temp_agent_results) 
 
results = pd.DataFrame.from_records(final_data) 
results_lvls = pd.DataFrame.from_records(final_data_fl_lvls) 
results.to_excel(r'/Users/civico/Desktop/Tentativi/SoloIE/Definitivi/Rule 3.xlsx') 
results_lvls.to_excel(r'/Users/civico/Desktop/Tentativi/SoloIE/Definitivi/3lvl.xlsx') 
print('Exported') 