import math
import decimal
from .models import Analysis

def get_contributions_of_members(project):
    contribution_per_member = []
    members = project.members.all().order_by('username')

    for current_evaluator in members:
        all_tsrs_received = []
        evaluatee_tsrs = list(project.tsr.all().filter(evaluator=current_evaluator).order_by('evaluatee'))
        if len(evaluatee_tsrs) == 0:
            return contribution_per_member

        recent_tsr_number = int(evaluatee_tsrs[-1].ass_number)

        for tsr_number in range(1, recent_tsr_number + 1):
            current_percent_contributions = []

            for current_tsr in evaluatee_tsrs:
                if int(current_tsr.ass_number) == tsr_number:
                    current_percent_contributions.append(float(current_tsr.percent_contribution))
            all_tsrs_received.append(current_percent_contributions)
        contribution_per_member.append(all_tsrs_received)
    return contribution_per_member

def similarity_of_eval_history(project, asgn_number):
    """
    Helper function that returns a dictionary of dictionaries
    reporting if each teammate's evaluations for team members are similar across all TSRs.
    """
    historic_similarities = {}
    members = project.members.all().order_by('username')
    marginofsimilarity = decimal.Decimal(0.1)


    for current_evaluator in members:
        evaluator_similarities = {}

        for current_evaluatee in members:
            evaluator_tsrs = list(project.tsr.all().filter(evaluatee=current_evaluatee, evaluator=current_evaluator))
            average_evaluation = 0
            num_evals_considered = 0
            for evaluation in evaluator_tsrs:
                if evaluation.ass_number <= asgn_number:
                    average_evaluation += evaluation.percent_contribution
                    num_evals_considered += 1

            average_evaluation /= num_evals_considered
            upper_bound = math.ceil(average_evaluation + (average_evaluation * marginofsimilarity))
            lower_bound = math.floor(average_evaluation - (average_evaluation * marginofsimilarity))

            for evaluation in evaluator_tsrs:
                if evaluation.ass_number <= asgn_number:
                    if lower_bound <= evaluation.percent_contribution <= upper_bound:
                        evaluator_similarities[current_evaluatee] = True
                    else:
                        evaluator_similarities[current_evaluatee] = False
        historic_similarities[current_evaluator] = evaluator_similarities
    for member in historic_similarities:
        hist_similar_count = 0
        #preconditions:(project , ([int]tsr_number, [User]associated_member , [string]analysis_type, [string]analysis_output))

        for evaluatee in historic_similarities[member]:
            if historic_similarities[member][evaluatee]:
                hist_similar_count += 1

        #preconditions:( AnalysisObject, [String]flag_detail)
        if hist_similar_count > 0:
            analysis_data = (asgn_number, member, "Historically Similar Scores", historic_similarities[member])
            analysis_object = setAnalysisData(project, analysis_data)
            setFlag(analysis_object, "%s has given %d sets of similar scores over time." % (member, hist_similar_count))
    return historic_similarities
    
def giving_outlier_scores(project, asgn_number):
    """
    Helper function that returns a dictionary of dictionaries of (member, low/high) pairs keyed
    to evaluator.
    """
    outlier_scores = {}
    members = project.members.all().order_by('username')
    low_bound, high_bound = ideal_score_ranges(project)
    for current_evaluator in members:
        evaluator_tsrs = list(project.tsr.all().filter(ass_number=asgn_number, evaluator=current_evaluator))
        evaluator_outliers = {}
        for evaluation in evaluator_tsrs:
            evaluatee = evaluation.evaluatee
            if evaluation.percent_contribution <= low_bound:
                evaluator_outliers[evaluatee] = 'Low'
            elif evaluation.percent_contribution >= high_bound:
                evaluator_outliers[evaluatee] = 'High'
        outlier_scores[current_evaluator] = evaluator_outliers
    
    for member in outlier_scores:
        low_count = 0
        high_count = 0
        #preconditions:(project , ([int]tsr_number, [User]associated_member , [string]analysis_type, [string]analysis_output))
        
        for evaluatee in outlier_scores[member]:
            if outlier_scores[member][evaluatee] == 'Low':
                low_count += 1
            elif outlier_scores[member][evaluatee] == 'High':
                high_count += 1
        #preconditions:( AnalysisObject, [String]flag_detail)
        if high_count > 0 or low_count > 0:
            analysis_data = (asgn_number, member, "Outlier Scores", outlier_scores[member])
            analysis_object = setAnalysisData(project, analysis_data)
            setFlag(analysis_object, "%s has given %d very low scores and %d very high scores." % (member, low_count, high_count))
       
    return outlier_scores
    
def ideal_score_ranges(project):
    members = project.members.all().order_by('username')
    ideal_average = math.floor(100/len(members))
    outlier_percentage = decimal.Decimal(0.5)
    low_bound = math.floor(ideal_average - (ideal_average * outlier_percentage))
    high_bound = math.ceil(ideal_average + (ideal_average * outlier_percentage))
    return (low_bound, high_bound)

def tsr_word_count(project, asgn_number):
    """
    Helper function that returns a dictionary of dictionaries of dictionaries of (pos/neg feedback, word count) pairs keyed
    to evaluatee keyed to evaluator.
    """
    word_counts = {}
    members = project.members.all().order_by('username')
    sparse_limit = 5
    verbose_limit = 20
    
    for current_evaluator in members:
        evaluator_tsrs = list(project.tsr.all().filter(ass_number=asgn_number, evaluator=current_evaluator))
        evaluator_word_counts = {}
        for evaluation in evaluator_tsrs:
            evaluatee = evaluation.evaluatee
            feedback_lengths = {}
            pos_feedback = evaluation.positive_feedback.split(None)
            neg_feedback = evaluation.negative_feedback.split(None)
            feedback_lengths['pos_feedback'] = len(pos_feedback)
            feedback_lengths['neg_feedback'] = len(neg_feedback)
            evaluator_word_counts[evaluatee] = feedback_lengths
        word_counts[current_evaluator] = evaluator_word_counts


    for member in word_counts:
        #preconditions:(project , ([int]tsr_number, [User]associated_member , [string]analysis_type, [string]analysis_output))
        sparse_count = 0
        verbose_count = 0

        for evaluatee in word_counts[member]:
            sparse_test = 0
            verbose_test = 0
            for feedback_type in word_counts[member][evaluatee]:
                if word_counts[member][evaluatee][feedback_type] < sparse_limit:
                    sparse_test += 1
                elif word_counts[member][evaluatee][feedback_type] > verbose_limit:
                    verbose_test += 1
            if sparse_test == 2:
                sparse_count += 1
            elif verbose_test > 1:
                verbose_count += 1

        if sparse_count > 0 or verbose_count > 0:
            analysis_data = (asgn_number, member, "Word Count", word_counts[member])
            analysis_object = setAnalysisData(project, analysis_data)
            setFlag(analysis_object, "%s has given %d sparse responses and %d verbose responses." % (member, sparse_count, verbose_count))

    return word_counts

def has_atleast_one_identical(member, total_report):
    for name in total_report:
        tuple_result = total_report[member][name]
        if tuple_result[0]:
            return True
    return False

def similarity_for_given_evals(project, asgn_number):
    """
    Helper function that returns a dictionary of dictionaries
    reporting if each teammate's evaluations of him/herself and others
    are similar across a range of particular TSRs.
    """
    all_similarities = {}
    members = project.members.all().order_by('username')
    marginofsimilarity = decimal.Decimal(0.1)

    for current_evaluator in members:
        evaluator_tsrs = list(project.tsr.all().filter(ass_number=asgn_number, evaluator=current_evaluator))
        evaluator_similarities = {}
        average_contribution = 0

        for evaluation in evaluator_tsrs:
            average_contribution += evaluation.percent_contribution
        average_contribution /= len(members)
        upper_bound = math.ceil(average_contribution + (average_contribution * marginofsimilarity))
        lower_bound = math.floor(average_contribution - (average_contribution * marginofsimilarity))

        for evaluation in evaluator_tsrs:
            evaluatee = evaluation.evaluatee
            if lower_bound <= evaluation.percent_contribution <= upper_bound:
                evaluator_similarities[evaluatee] = (True, evaluation.percent_contribution)
            else:
                evaluator_similarities[evaluatee] = (False, evaluation.percent_contribution)
        all_similarities[current_evaluator] = evaluator_similarities

    for member in all_similarities:
        if has_atleast_one_identical(member, all_similarities):
            analysis_data = (asgn_number, member, "Similarity for Given Evaluations",
                             all_similarities[member])
            analysis_flags = "%s has been giving very similar scores to other team members." % member
            analysis_object = setAnalysisData(project, analysis_data)
            setFlag(analysis_object, analysis_flags)
    return all_similarities

def averages_for_all_evals(project, asgn_number):
    """
    Helper function that returns a dictionary of averages for percent
    contributions for each team member in a project.
    """
    member_averages = {}
    members = project.members.all().order_by('username')

    for current_evaluatee in members:
        evaluatee_tsrs = list(project.tsr.all().filter(evaluatee=current_evaluatee))
        average_contribution = 0
        num_evals_considered = 0
        for evaluation in evaluatee_tsrs:
            if evaluation.ass_number <= asgn_number:
                average_contribution += evaluation.percent_contribution
                num_evals_considered += 1

        if num_evals_considered == 0:
            return member_averages

        bounds = ideal_score_ranges(project)
        member_averages[current_evaluatee] = round(average_contribution / num_evals_considered, 1)
        analysis_data = (asgn_number, current_evaluatee, "Averages for all Evaluations",
                         member_averages[current_evaluatee])
        analysis_object = setAnalysisData(project, analysis_data)
        # bounds[1] is the high bound.
        if member_averages[current_evaluatee] >= bounds[1]:
            analysis_flag = "%s has a higher than typical average score." % current_evaluatee
            setFlag(analysis_object, analysis_flag)
        # bounds[0] is the low bound.
        elif member_averages[current_evaluatee] <= bounds[0]:
            analysis_flag = "%s has a lower than typical average score." % current_evaluatee
            setFlag(analysis_object, analysis_flag)

    return member_averages

def numerical_averages_for_all_evals(project, asgn_number):
    """
    Helper function that returns a dictionary of averages for percent
    contributions for each team member in a project.
    """
    member_averages = {}
    members = project.members.all().order_by('username')

    for current_evaluatee in members:
        evaluatee_tsrs = list(project.tsr.all().filter(evaluatee=current_evaluatee, ass_number=asgn_number))
        average_contribution = 0
        for evaluation in evaluatee_tsrs:
            average_contribution += evaluation.percent_contribution

        member_averages[current_evaluatee.username] = round(average_contribution / len(evaluatee_tsrs), 1)
    return member_averages

def calculate_member_averages(project, assigned_tsrs):
    members = project.members.all().order_by('username')

    member_averages = []
    tsr_numbers = []
    highest_tsr_number = 0
    for tsr in assigned_tsrs:
        if highest_tsr_number < tsr.ass_number:
            highest_tsr_number = tsr.ass_number
    for current_tsr_number in range(1, highest_tsr_number + 1):
        completed_tsrs_per_ass_number = project.tsr.filter(ass_number=current_tsr_number)
        if len(members) != 0 and len(members) == (len(completed_tsrs_per_ass_number)/len(members)):
            averages_dict = numerical_averages_for_all_evals(project, current_tsr_number)
            averages_floats = []
            for member in averages_dict:
                averages_floats.append(float(averages_dict[member]))
            member_averages.append(averages_floats)
            tsr_numbers.append(current_tsr_number)
    return member_averages, tsr_numbers

def calculate_health_score(project):
    members = project.members.all().order_by('username')

    local_similarity_weight = 1
    outlier_weight = 5
    wordcount_weight = 1
    historical_similarity_weight = 2
    averages_weight = 5

    health_report_total = 0
    health_ideal = (outlier_weight ^ 2) + wordcount_weight * len(members)
    # 0 is good, 1 is warning, 2 is bad
    health_flag = 0
    analysis_dicts = {}

    for analysis_object in project.analysis.all():
        analysis_dicts.setdefault(analysis_object.analysis_type, []).append([analysis_object])
        if analysis_object.analysis_type == "Historically Similar Scores":
            health_report_total += historical_similarity_weight
        elif analysis_object.analysis_type == "Outlier Scores":
            health_report_total += outlier_weight
        elif analysis_object.analysis_type == "Word Count":
            health_report_total += wordcount_weight
        elif analysis_object.analysis_type == "Similarity for Given Evaluations":
            health_report_total += local_similarity_weight
        elif analysis_object.analysis_type == "Averages for all Evaluations":
            health_report_total += averages_weight

    if health_report_total < health_ideal:
        health_flag = 0
    elif health_report_total >= health_ideal:
        health_flag = 2
    analysis_items = analysis_dicts.items()

    return analysis_items, health_flag

#the wrapper function : gets current project and data and saves it to correct project
#preconditions:(project , ([int]tsr_number, [User]associated_member , [string]analysis_type, [string]analysis_output)
def setAnalysisData(project, analysisData):
    analysis = Analysis()
    analysis.tsr_number = analysisData[0]
    analysis.associated_member = analysisData[1]
    analysis.analysis_type = analysisData[2]
    analysis.analysis_output = analysisData[3]
    analysis.save()
                 
    #saving in manytomany field project
    project.analysis.add(analysis)
    project.save()

    return analysis


#the wrapper function :updates the piece of analysis with the correct flag information
#preconditions:( AnalysisObject, ([boolean] flag_tripped, [String]flag_detail))
def setFlag(analysis_object, flag_details):
    analysis_object.flag_detail = flag_details
    analysis_object.save()
