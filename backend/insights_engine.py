# /backend/insights_engine.py
import random


def generate_insights(user_personality, user_principles, latest_checkin):
    """
    Runs a simple rules-based engine to generate insights.

    :param user_personality:
        List of user's personality traits (from personality_traits table)
    :param user_principles:
        List of user's principles (from user_principles table)
    :param latest_checkin:
        The latest check-in data (from daily_checkins & metrics)
    :return:
        A string containing a generated insight, or None.
    """

    insights = []

    # --- Rule 1:
    # Check Principle Alignment ---
    alignment_score = latest_checkin.get('principle_alignment')
    if alignment_score is not None and alignment_score < 5:
        insights.append(
            f"Your principle alignment score was {alignment_score}/10. "
            f"Remember your note:\n\n"
            f"{latest_checkin.get('principle_alignment_note')}. "
            "What's one small action you can take today to align better?"
        )

    # --- Rule 2:
    # Check for a specific personality trait (e.g., Introverted) ---
    is_introverted = any(p['trait_name'] == 'Introverted' and p['value'] >= 60
                         for p in user_personality)

    # --- Rule 3:
    # Check for a specific metric (e.g., Social Time) ---
    social_time = 0
    for metric in latest_checkin.get('metrics', []):
        if metric.get('metric_name') == 'Social' \
                      and metric.get('metric_type') == 'Time Allocation':
            social_time = metric.get('value', 0)
            break

    # --- Rule 4:
    # Combine Personality and Metrics ---
    if is_introverted and social_time < 5:
        insights.append(
            "As an introvert, solo time is key, \
            but you've logged very little social time. \
            Remember that even small, \
            positive interactions can boost your energy."
        )

    # --- Rule 5:
    # Check Gratitude ---
    if not latest_checkin.get('gratitude_entry'):
        insights.append(
            "You didn't log a gratitude entry yesterday. "
            "Try to spot one small thing you're thankful for right now."
        )

    # --- If no specific rules hit, give a generic insight ---
    if not insights:
        insights.append("Keep up the great work. \
                        Consistency is the key to progress.")

    # Select one insight at random to show the user
    return random.choice(insights)
