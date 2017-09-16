# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:02:12 2017

@author: jununez
"""
import pandas as pd
import numpy as np

class BaseTree(object):
    
    def __init__(self,X,target,max_depth = 3,min_size = 2,root = None):
        #X is a pandas dataframe. y is a string. Root is a dict. Nice docs I know.
        
        self.X = X
        self.target = target
        self.max_depth = max_depth
        self.min_size = min_size
        self.condition_list = {}
        self.root = None
        
        
    
    def Parse_Value(self,value):
        if "." in value:
            return float(value)
        try:
            return int(value)
        except:
            return value

    
    def Create_Split(self,data,split_column):
        splits = []
        values = data[split_column].unique()
        if data[split_column].dtype == object or len(values) <= 3:
            #It's either a categorical column or a binary column.

            if len(values) == 2:
                values = [values[0]]
            for value in values:
                left_split = data.loc[data[split_column] == value]
                right_split = data.loc[data[split_column]!= value]
                split_name = split_column + " = " + str(value)
                splits.append([left_split,right_split,split_name])
        else:
            #It's a numerical column.
            if len(values) >= 20:
                perts = np.arange(0.1,1.0,0.1)
                summary = data[split_column].describe(perts)
                pert_names = ["{}%".format(int(i*100)) for i in perts if i !=0.3]
                pert_names.append("30.0%") #force
                pert_names.remove("30%") #force
                values = summary[pert_names]
            
            for value in values:
                left_split = data.loc[data[split_column] <= value]
                right_split = data.loc[data[split_column] > value]
                split_name = split_column + " <= " + str(value)
                splits.append([left_split,right_split,split_name])
            
        return splits
    
    
    def Print_Tree(self,Node, depth=0):
        if isinstance(Node, dict):
            print('{}  {} : {}'.format( depth * ' ',depth,Node['condition']))
            self.Print_Tree(Node['left'], depth+1)
            self.Print_Tree(Node['right'], depth+1)
        else:
            print('{}  {} : {}'.format(depth * ' ',depth,Node))
      
    
    def Predict(self,data):
        preds = [None] * len(data)
        return self.Traverse(preds,self.root,data)
    
    def Traverse(self,preds,Node,data):
        if isinstance(Node,dict):
            condition = Node['condition'].split()
            column = condition[0]
            comparison = condition[1]
            value = self.Parse_Value(condition[2])
            
            if comparison == "=":
                left_data = data.loc[data[column] == value]
                right_data = data.loc[data[column] != value]
                self.Traverse(preds,Node['left'],left_data)
                self.Traverse(preds,Node['right'],right_data)
            else:
                left_data = data.loc[data[column] <= value]
                right_data = data.loc[data[column] > value]
                self.Traverse(preds,Node['left'],left_data)
                self.Traverse(preds,Node['right'],right_data)
            
        else:
            for i in data.index:
                preds[i] = Node
        
        return preds
        
        
class ClassificationTree(BaseTree):
    
    def __init__(self,X,target,max_depth = 3,min_size = 2,root = None):
        super().__init__(X,target,max_depth,min_size,root)
        self.class_values = list(X[target].unique())
        
    
    
    def Gini(self,groups):
        gini = 0.0
        for value in self.class_values:
            for group in groups:
                group_size = group.shape[0]
                split = group.loc[group[self.target] == value]
                split_size = split.shape[0]
                if split_size > 0:
                    proportion = split_size / group_size
                    gini += proportion * (1 - proportion)
        return gini
    
    

    
    
    def Get_Best_Column_Split(self,data,verbose = False):
        temp = data.drop(self.target, axis = 1).copy()
        best_gini = 100
        best_split_condition = ""
        best_split = {}
        for column in temp.columns:
            column_splits = self.Create_Split(data,column)
            if len(column_splits) == 1:
                split = column_splits[0]
                best_split_condition = split[2]
                best_split["left"] = split[0]
                best_split["right"] = split[1]
                best_split["condition"] = best_split_condition
            
            for split in column_splits:
                split_gini = self.Gini(split[0:2])
                if verbose:
                    print("Splitting : " + split[2] + " Gini : " + str(split_gini))
                if split_gini < best_gini and split[2] not in self.condition_list:
                    best_gini = split_gini
                    best_split_condition = split[2]
                    best_split["left"] = split[0]
                    best_split["right"] = split[1]
                    best_split["condition"] = best_split_condition
                    
        if verbose:
            print("Best split: " + best_split_condition + " best Gini: " + str(best_gini))
        self.condition_list[best_split_condition] = True
        return best_split
    
    def terminal_node(self,group):
        outcomes = group[self.target].value_counts()
        return outcomes.index[0]
    
    def Split_Tree(self,split,cur_depth,verbose = False):
        left,right = split["left"],split["right"]
        #In case our depth is too large.
        del split["left"]
        del split["right"]
        
        if  len(left) == 0 or len(right) == 0:
            split["left"] = split["right"] = self.terminal_node((left.append(right)))
            return
        if cur_depth == self.max_depth:
            split["left"], split["right"] = self.terminal_node(left), self.terminal_node(right)
            return
        #Calculate left
        if len(left) <= self.min_size:
            split["left"] = self.terminal_node(left)
        else:
            split["left"] = self.Get_Best_Column_Split(left,verbose = verbose)
            self.Split_Tree(split["left"],cur_depth + 1,verbose = verbose)
        
        #Calculate right
        if len(right) <= self.min_size:
            split["right"] = self.terminal_node(right)
        else:
            split["right"] = self.Get_Best_Column_Split(right,verbose = verbose)
            self.Split_Tree(split["right"],cur_depth + 1,verbose= verbose)
    
    def Build_Tree(self,verbose = False):
        self.root = self.Get_Best_Column_Split(self.X, verbose = verbose)
        self.Split_Tree(self.root,1,verbose = verbose)
        
        
class RegressionTree(BaseTree):
    
    def __init__(self,X,target,max_depth = 3,min_size = 2,root = None):
        super().__init__(X,target,max_depth,min_size,root)
    
    
    def SdevReduction(self,groups,sdev):
        best_sdev = 0
        for group in groups:
            groupsdev = group[self.target].std()
            diff = sdev - groupsdev
            if diff > best_sdev:
                best_sdev = diff
                
        return best_sdev
    
    def Get_Best_Column_Split(self,data,verbose = False):
        temp = data.drop(self.target, axis = 1).copy()
        best_sdev = 0
        best_split_condition = ""
        best_split = {}
        orig_sdev = data[self.target].std()
        for column in temp.columns:
            column_splits = self.Create_Split(data,column)
            if len(column_splits) == 1:
                split = column_splits[0]
                best_split_condition = split[2]
                best_split["left"] = split[0]
                best_split["right"] = split[1]
                best_split["condition"] = best_split_condition
            for split in column_splits:
                split_sdev = self.SdevReduction(split[0:2],orig_sdev)
                if verbose:
                    print("Splitting : " + split[2] + " SDEV : " + str(split_sdev))
                if split_sdev >= best_sdev and split[2] not in self.condition_list:
                    best_sdev = split_sdev
                    best_split_condition = split[2]
                    best_split["left"] = split[0]
                    best_split["right"] = split[1]
                    best_split["condition"] = best_split_condition
                    
        if verbose:
            print("Best split: " + best_split_condition + " best SDEV: " + str(best_sdev))
        self.condition_list[best_split_condition] = True
        return best_split
    
    def terminal_node(self,group):
        return group[self.target].mean()

    def Split_Tree(self,split,cur_depth,verbose = False):
        left,right = split["left"],split["right"]
        #In case our depth is too large.
        del split["left"]
        del split["right"]
        
        if  len(left) == 0 or len(right) == 0:
            split["left"] = split["right"] = self.terminal_node((left.append(right)))
            return
        
        if cur_depth == self.max_depth:
            split["left"], split["right"] = self.terminal_node(left), self.terminal_node(right)
            return
        #Calculate left
        if len(left) <= self.min_size:
            split["left"] = self.terminal_node(left)
        else:
            split["left"] = self.Get_Best_Column_Split(left,verbose = verbose)
            self.Split_Tree(split["left"],cur_depth + 1,verbose = verbose)
        
        #Calculate right
        if len(right) <= self.min_size:
            split["right"] = self.terminal_node(right)
        else:
            split["right"] = self.Get_Best_Column_Split(right,verbose = verbose)
            self.Split_Tree(split["right"],cur_depth + 1,verbose= verbose)
            
            
    def Build_Tree(self,verbose = False):
        self.root = self.Get_Best_Column_Split(self.X, verbose = verbose)
        self.Split_Tree(self.root,1,verbose = verbose)
        