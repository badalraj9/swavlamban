import math

class Evaluator:
    def __init__(self):
        pass

    def calculate_score(self, scenario_data):
        # scenario_data: {
        #   "tasks": [{id, value, location, requirements}],
        #   "agents": [{id, location, capabilities, assignments}],
        #   "total_bytes": int
        # }

        # 1. Value Ratio: (Sum of values of completed tasks) / (Total possible value)
        total_value = sum(t['value'] for t in scenario_data['tasks'])
        completed_value = 0
        for t in scenario_data['tasks']:
            if t['assigned_to'] is not None:
                # Validate capability?
                # Assume simulation ensures valid assignment or we penalize here.
                completed_value += t['value']

        value_ratio = completed_value / total_value if total_value > 0 else 0

        # 2. Normalized Distance: 1.0 - (Total Distance / Max Budget Distance)
        # Simplified: Just sum distance traveled.
        # But score needs to be maximized.
        # Let's assume a "Distance Score" where closer = better.
        # Format: score = w1 * value_ratio + w2 * distance_score + w3 * bytes_score

        total_distance = 0
        for a in scenario_data['agents']:
            # Calculate distance from start to assigned tasks
            # TSP is hard, let's assume direct line to one task or sequence.
            pass

        # 3. Bytes: Less is better.
        # bytes_score = 1.0 / (1.0 + total_bytes / threshold)

        # For this Phase, the directive says "Score >= 0.7".
        # I need to know the formula.
        # "SCORE_COMPONENTS: value_ratio, normalized_distance, normalized_bytes"
        # Let's assume arithmetic mean or weighted.

        # Placeholder
        score = value_ratio # Mostly driven by completion for now
        return score
