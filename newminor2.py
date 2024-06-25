import random
import copy

MAX_DAYS = 7
MAX_NAME_LENGTH = 50
MAX_SUBJECT_LENGTH = 50
MAX_DIVISIONS = 5
POPULATION_SIZE = 20
MUTATION_RATE = 0.2
NUM_GENERATIONS = 100

# Class definitions
class Class:
    def __init__(self, name, time, faculty, subject, division, classroom):
        self.name = name
        self.time = time
        self.faculty = faculty
        self.subject = subject
        self.division = division
        self.classroom = classroom

class Timetable:
    def __init__(self):
        self.classes = [[] for _ in range(MAX_DAYS)]
        self.num_classes = [0] * MAX_DAYS

class Subject:
    def __init__(self, name, faculty):
        self.name = name
        self.faculty = faculty

# Function to generate class name
def generate_class_name(subject, faculty, division):
    return f"{subject.name}{faculty}{division}"

# Function to simulate input form and generate initial population of timetables
def generate_initial_population(professors, subjects, divisions, population_size):
    population = []
    for _ in range(population_size):
        timetables = round_robin_scheduling(professors, subjects, divisions)
        population.append(timetables)
    return population

# Round robin scheduling function
def round_robin_scheduling(professors, subjects, divisions):
    timetables = {}
    classrooms = {}  # Dictionary to store classrooms for each division

    # Simulate classroom input for each division
    for division in range(1, divisions + 1):
        classrooms[division] = f"Classroom_{division}"

    # Define time slots for each day, excluding break times
    time_slots = [
        [],  # Sunday (Holiday)
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],  # Monday
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],  # Tuesday
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],  # Wednesday
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],  # Thursday
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],  # Friday
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM"]  # Saturday (Half Day)
    ]

    # Initialize counters for each faculty member
    faculty_counters = {faculty_name: 0 for faculty_name in professors}

    for division in range(1, divisions + 1):
        timetable = Timetable()
        timetables[division] = timetable

    for day in range(1, MAX_DAYS):  # Start from Monday (index 1)
        for time_slot in range(len(time_slots[day])):
            for division in range(1, divisions + 1):
                # Get the faculty member to assign the class to (round-robin)
                faculty_name = professors[(day * len(time_slots[day]) * divisions + time_slot * divisions + division) % len(professors)]

                # Randomly select a subject from the list associated with the faculty
                subject = random.choice(subjects[faculty_name])

                # Generate a unique class name
                class_name = generate_class_name(subject, faculty_name, division)

                # Create the class and add it to the timetable
                class_ = Class(class_name, time_slots[day][time_slot], faculty_name, subject.name, division, classrooms[division])
                timetables[division].classes[day].append(class_)
                timetables[division].num_classes[day] += 1

                # Increment the counter for the assigned faculty member
                faculty_counters[faculty_name] += 1

    return timetables

# Fitness function (example, needs customization based on specific constraints)
def fitness_function(timetables):
    fitness = 0
    for division, timetable in timetables.items():
        for day in range(1, MAX_DAYS):
            for class_ in timetable.classes[day]:
                # Example fitness criteria: penalize overlapping classes
                if timetable.num_classes[day] > 1:
                    fitness -= 1
                # You can add more criteria based on room capacity, balanced workload, etc.
                # Adjust fitness calculation as per specific requirements
    return fitness

# Tournament selection
def tournament_selection(population, tournament_size):
    selected = []
    for _ in range(len(population)):
        participants = random.sample(population, tournament_size)
        winner = max(participants, key=lambda x: fitness_function(x))
        selected.append(copy.deepcopy(winner))
    return selected

# Crossover (two-point crossover)
def crossover(parent1, parent2):
    point1 = random.randint(1, MAX_DAYS - 1)
    point2 = random.randint(point1, MAX_DAYS - 1)

    child1 = {}
    child2 = {}

    # Iterate over the divisions that actually exist in the parents
    for division in parent1.keys():  # Assuming parent1 and parent2 have the same divisions
        child1[division] = Timetable()
        child2[division] = Timetable()

        for day in range(1, MAX_DAYS):
            if day < point1 or day >= point2:
                child1[division].classes[day] = copy.deepcopy(parent1[division].classes[day])
                child2[division].classes[day] = copy.deepcopy(parent2[division].classes[day])
            else:
                child1[division].classes[day] = copy.deepcopy(parent2[division].classes[day])
                child2[division].classes[day] = copy.deepcopy(parent1[division].classes[day])

    return child1, child2

# Mutation (swap mutation)
def mutate(timetable):
    # Iterate over the divisions that actually exist in the timetable
    for division in timetable.keys(): 
        for day in range(1, MAX_DAYS):
            if random.random() < MUTATION_RATE:
                # Perform swap mutation on classes within the same day
                num_classes = len(timetable[division].classes[day])
                if num_classes > 1:
                    idx1, idx2 = random.sample(range(num_classes), 2)
                    timetable[division].classes[day][idx1], timetable[division].classes[day][idx2] = \
                        timetable[division].classes[day][idx2], timetable[division].classes[day][idx1]

    return timetable

# Genetic algorithm main loop
def genetic_algorithm(professors, subjects, divisions):
    population = generate_initial_population(professors, subjects, divisions, POPULATION_SIZE)

    for generation in range(NUM_GENERATIONS):
        print(f"Generation {generation + 1}/{NUM_GENERATIONS}")
        
        # Selection
        selected_population = tournament_selection(population, tournament_size=5)

        # Crossover
        offspring_population = []
        for i in range(0, len(selected_population), 2):
            parent1 = selected_population[i]
            parent2 = selected_population[i + 1]
            child1, child2 = crossover(parent1, parent2)
            offspring_population.append(mutate(child1))
            offspring_population.append(mutate(child2))

        # Replacement (Elitism: Replace the worst individuals with the offspring)
        population = sorted(population, key=lambda x: fitness_function(x), reverse=True)[:POPULATION_SIZE - len(offspring_population)]
        population.extend(offspring_population)

    # Return the best timetable found in the final population
    best_timetable = max(population, key=lambda x: fitness_function(x))
    return best_timetable

# Function to simulate input form and generate timetables
def generate_timetables():
    # Input number of professors
    num_professors = int(input("Enter number of professors: "))
    
    professors = []
    subjects = {}

    # Input professors and their subjects
    for i in range(num_professors):
        professor_name = input(f"Enter name of professor {i + 1}: ")
        professors.append(professor_name)

        num_subjects = int(input(f"Enter number of subjects for {professor_name}: "))
        subjects[professor_name] = []

        for j in range(num_subjects):
            subject_name = input(f"Enter name of subject {j + 1} for {professor_name}: ")
            subjects[professor_name].append(Subject(subject_name, professor_name))

    # Input number of divisions
    divisions = int(input("Enter number of divisions: "))

    # Generate timetables using genetic algorithm
    best_timetable = genetic_algorithm(professors, subjects, divisions)

    return best_timetable

# Example usage:
if __name__ == "__main__":
    timetables = generate_timetables()

    # Print the best generated timetable
    for division, timetable in timetables.items():
        print(f"Timetable for Division {division}:")
        for day in range(1, MAX_DAYS):
            print(f"  Day {day}:")
            for class_ in timetable.classes[day]:
                print(f"    {class_.time} - {class_.name} (Subject: {class_.subject}, Faculty: {class_.faculty}, Classroom: {class_.classroom})")
