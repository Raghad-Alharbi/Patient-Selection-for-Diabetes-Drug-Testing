import pandas as pd
import numpy as np
import os
import tensorflow as tf
import functools

####### STUDENTS FILL THIS OUT ######
#Question 3
def reduce_dimension_ndc(df, ndc_df):
    '''
    df: pandas dataframe, input dataset
    ndc_df: pandas dataframe, drug code dataset used for mapping in generic names
    return:
        df: pandas dataframe, output dataframe with joined generic drug name
    '''
    ndc_df = ndc_df[['NDC_Code', 'Non-proprietary Name']] # we only need the names not the whole table
    ndc_df.columns = ['ndc_code', 'generic_drug_name'] # changing the columns names for easier merge
    
    temp_df = df.copy()
    temp_df = temp_df.merge(ndc_df, on="ndc_code", how="left")

    return temp_df


#Question 4
def select_first_encounter(df):
    '''
    df: pandas dataframe, dataframe with all encounters
    return:
        - first_encounter_df: pandas dataframe, dataframe with only the first encounter for a given patient
    '''
    first_encounter_df = df.sort_values('encounter_id').drop_duplicates(subset='patient_nbr', keep="first").reset_index(drop = True)
    return first_encounter_df
    

    


#Question 6
def patient_dataset_splitter(df, patient_key='patient_nbr'):
    '''
    df: pandas dataframe, input dataset that will be split
    patient_key: string, column that is the patient id

    return:
     - train: pandas dataframe,
     - validation: pandas dataframe,
     - test: pandas dataframe,
    '''
    keys = df[patient_key].values
    np.random.seed(seed= 42)
    keys = np.random.permutation(keys)
    
    size = len(keys)
    train_size = int(0.6*size) # 60% train
    validation_size = int(0.2*size) # 20% valid and 20% test

    train_keys = keys[:train_size]
    validation_keys = keys[train_size:train_size+validation_size]
    test_keys = keys[train_size+validation_size:]

    train = df[df[patient_key].isin(train_keys)]
    validation = df[df[patient_key].isin(validation_keys)]
    test = df[df[patient_key].isin(test_keys)]

    print("Total number of unique patients in train = ", len(train['patient_nbr'].unique()))
    print("Total number of unique patients in valid = ", len(validation['patient_nbr'].unique()))
    print("Total number of unique patients in test = ", len(test['patient_nbr'].unique()))
    
    print("\nTraining partition has a shape = ", train.shape) 
    print("Validation partition has a shape = ", validation.shape) 
    print("Test partition has a shape = ", test.shape)
    
    return train, validation, test

#Question 7

def create_tf_categorical_feature_cols(categorical_col_list,
                              vocab_dir='./diabetes_vocab/'):
    '''
    categorical_col_list: list, categorical field list that will be transformed with TF feature column
    vocab_dir: string, the path where the vocabulary text files are located
    return:
        output_tf_list: list of TF feature columns
    '''
    output_tf_list = []
    for c in categorical_col_list:
        vocab_file_path = os.path.join(vocab_dir,  c + "_vocab.txt")
        '''
        Which TF function allows you to read from a text file and create a categorical feature
        You can use a pattern like this below...
        tf_categorical_feature_column = tf.feature_column.......

        '''
        tf_categorical_feature_column = tf.feature_column.categorical_column_with_vocabulary_file( key=c, vocabulary_file = vocab_file_path, num_oov_buckets=1)
        
        tf_categorical_feature_column = tf.feature_column.indicator_column(tf_categorical_feature_column)
        output_tf_list.append(tf_categorical_feature_column)
    return output_tf_list

#Question 8
def normalize_numeric_with_zscore(col, mean, std):
    '''
    This function can be used in conjunction with the tf feature column for normalization
    '''
    return (col - mean)/std



def create_tf_numeric_feature(col, MEAN, STD, default_value=0):
    '''
    col: string, input numerical column name
    MEAN: the mean for the column in the training data
    STD: the standard deviation for the column in the training data
    default_value: the value that will be used for imputing the field

    return:
        tf_numeric_feature: tf feature column representation of the input field
    '''
    normalizer = functools.partial(normalize_numeric_with_zscore, mean = MEAN, std = STD)
    tf_numeric_feature = tf.feature_column.numeric_column(key = col, 
                                                      default_value = 0, 
                                                      normalizer_fn = normalizer, 
                                                      dtype = tf.float64)
    return tf_numeric_feature

#Question 9
def get_mean_std_from_preds(diabetes_yhat):
    '''
    diabetes_yhat: TF Probability prediction object
    '''
    m = diabetes_yhat.mean()
    s = diabetes_yhat.stddev()
    return m, s

# Question 10
def get_student_binary_prediction(df, col, threshold ):
    '''
    df: pandas dataframe prediction output dataframe
    col: str,  probability mean prediction field
    return:
        student_binary_prediction: pandas dataframe converting input to flattened numpy array and binary labels
    '''
    student_binary_prediction = np.where(df[col] > threshold, 1, 0)
    
    return student_binary_prediction
