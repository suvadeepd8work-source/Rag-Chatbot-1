import os
import json
import re

DATA_DIR = os.path.join("Phase_1_Data_Acquisition", "scraped_data")
OUTPUT_DIR = "Phase_2_Vector_Database"
AGGREGATED_FILE = os.path.join(OUTPUT_DIR, "courses.json")
CHUNKS_FILE = os.path.join(OUTPUT_DIR, "course_chunks.json")

def aggregate_data():
    all_courses = []
    if not os.path.exists(DATA_DIR):
        print(f"Data directory {DATA_DIR} not found.")
        return []
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json") and filename != "courses.json":
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Add course name from filename if not present
                course_name = filename.replace(".json", "").replace("_", " ").title()
                data["course_name"] = course_name
                all_courses.append(data)
                
    with open(AGGREGATED_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_courses, f, indent=2)
    
    print(f"Aggregated {len(all_courses)} courses into {AGGREGATED_FILE}")
    return all_courses

def create_chunks(courses):
    chunks = []
    for course in courses:
        name = course.get("course_name", "Unknown Course")
        url = course.get("source_url", "https://nextleap.app")
        
        # 1. Overview Chunk
        overview = f"Course: {name}\n"
        overview += f"Duration: {course.get('duration')}\n"
        overview += f"Live Classes: {course.get('live_hours')}\n"
        overview += f"Cohort Starts: {course.get('cohort_start')}\n"
        if course.get('cost'):
            overview += f"Cost: ₹{course.get('cost')}"
            if course.get('original_cost'):
                overview += f" (Discounted from ₹{course.get('original_cost')})"
            overview += "\n"
        if course.get('emi'):
            overview += f"EMI: Starts from ₹{course.get('emi')}/month\n"
        
        chunks.append({
            "content": overview,
            "metadata": {
                "course": name,
                "url": url,
                "type": "overview"
            }
        })
        
        # 2. Instructors Chunk
        if course.get("instructors"):
            instr_text = f"Instructors for {name}:\n"
            instr_text += "\n".join([f"- {instr}" for instr in course["instructors"]])
            chunks.append({
                "content": instr_text,
                "metadata": {
                    "course": name,
                    "url": url,
                    "type": "instructors"
                }
            })
            
        # 3. Schedule Chunk
        if course.get("live_schedule"):
            chunks.append({
                "content": f"Live Class Schedule for {name}:\n{course['live_schedule']}",
                "metadata": {
                    "course": name,
                    "url": url,
                    "type": "schedule"
                }
            })
            
        # 4. Salary/Placement Chunk
        if course.get("average_salary") or course.get("highest_salary") or course.get("placement_support"):
            sal_text = f"Placement and Salary info for {name}:\n"
            if course.get("placement_support"):
                sal_text += f"- Placement Support: {course['placement_support']}\n"
            if course.get("average_salary"):
                sal_text += f"- Average Salary: {course['average_salary']}\n"
            if course.get("highest_salary"):
                sal_text += f"- Highest Salary: {course['highest_salary']}\n"
            
            chunks.append({
                "content": sal_text,
                "metadata": {
                    "course": name,
                    "url": url,
                    "type": "outcomes"
                }
            })

    with open(CHUNKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2)
    
    print(f"Created {len(chunks)} chunks into {CHUNKS_FILE}")

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    courses = aggregate_data()
    if courses:
        create_chunks(courses)
