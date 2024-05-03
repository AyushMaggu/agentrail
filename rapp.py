from urllib.parse import uses_query
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from geminichain import geminichain
from datetime import datetime
import time
import re
import os


### Add the condition at the appropriate place about what to do after a ticket has been booked and 
### Firefox browser has moved forward.  
#os.environ['MOZ_HEADLESS'] = '1'
### Use : os.environ.pop('MOZ_HEADLESS') to remove the firefox headless state after certain period of time.
### There are two ways to book train ticket routing fucntionality. First : 


# Function to extract the longest capital substring
def extract_longest_capital_substring(text):
    longest_substring = ""
    current_substring = ""

    for char in text:
        if char.isupper():
            current_substring += char
        else:
            if len(current_substring) > len(longest_substring):
                longest_substring = current_substring
            current_substring = ""

    # Check the last substring
    if len(current_substring) > len(longest_substring):
        longest_substring = current_substring
    return longest_substring


# Function to fetch train details using Selenium
def fetch_train_details(origin, destination, travel_date):
    
    # os.environ['MOZ_HEADLESS'] = '1'
    url = "https://www.makemytrip.com/railways/listing?classCode=&className=All%20Classes&date=20240430&destCity=Mumbai&destStn=CSTM&srcCity=Delhi&srcStn=NDLS"
    options = Options()
    driver = webdriver.Firefox(options=options)
    #options.headless = True
    driver.get(url)
    driver.maximize_window()
    time.sleep(1)

    # Selecting Origin City
    origin_station = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "rsw_inputField"))
    )
    origin_station.send_keys(origin)
    time.sleep(2)
    dropdown_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#react-autowhatever-1-section-0-item-0"))
    )
     
    time.sleep(2)
    if dropdown_option:
        first_option_origin = dropdown_option.text
        dropdown_option.click()

    time.sleep(1)

    # Selecting Destination City
    destination_station = driver.find_elements(By.CLASS_NAME, "rsw_inputField")[1]
    destination_station.send_keys(destination)
    time.sleep(2)
    dropdown_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#react-autowhatever-1-section-0-item-0"))
    )
    first_option_destination = dropdown_option.text
    dropdown_option.click()

    driver.quit()

    # Collating travel details for the final URL link and opening it
    origin_formatted = first_option_origin.split(',')[0]
    destination_formatted = first_option_destination.split(',')[0]

    origin_code = extract_longest_capital_substring(first_option_origin)
    destination_code = extract_longest_capital_substring(first_option_destination)
    

    url1 = 'https://makemytrip.com/railways/listing?classCode=&className=All%20Classes&'
    url2 = 'date={}_find&destCity={}&destStn={}&srcCity={}&srcStn={}'.format(travel_date, destination_formatted, destination_code, origin_formatted, origin_code)
    url = url1 + url2

    driver = webdriver.Firefox()
    driver.get(url)
    driver.maximize_window() 
    #driver.minimize_window()

    button = driver.find_elements(By.CLASS_NAME, "primaryBtn")[0]
    button.click()
    time.sleep(2)

    # Initialize an empty string to store train details
    num_of_trains = 0
    train_details_string = ""
    links = {}
    # Find all train details elements
    train_details_elements = driver.find_elements(By.CLASS_NAME, "single-train-detail")

    # Iterate over each train details element to extract information
    for train_details_element in train_details_elements:
        num_of_trains += 1
        # Extract train details
        train_name = train_details_element.find_element(By.CLASS_NAME, 'train-name').text.strip()
        train_depart_number = train_details_element.find_element(By.CSS_SELECTOR, '.train-depart-number div').text.strip()
        departs_on = train_details_element.find_element(By.CSS_SELECTOR, '.train-depart-number').text.strip()
        departure_time = train_details_element.find_element(By.CLASS_NAME, 'depart-time').text.strip()
        departure_station = train_details_element.find_element(By.CLASS_NAME, 'station-name').text.strip()
        right_info_element = train_details_element.find_element(By.CLASS_NAME, "right-info")
        arrival_time = right_info_element.find_element(By.CSS_SELECTOR, '.arrival-time').text.strip()
        arrival_station = right_info_element.find_elements(By.CLASS_NAME, 'station-name')[1].text.strip()
        
        train_details_string += f"Train Element Number : {num_of_trains}\n"
        train_details_string += f"Train Name: {train_name}\n"
        train_details_string += f"Train Departure Number: {train_depart_number}\n"
        train_details_string += f"Departs on: {departs_on}\n"
        train_details_string += f"Departure Time: {departure_time}\n"
        train_details_string += f"Departure Station: {departure_station}\n"
        train_details_string += f"Arrival Time: {arrival_time}\n"
        train_details_string += f"Arrival Station: {arrival_station}\n"

        # Find all rail class, availability, and ticket price elements
        rail_class_elements = train_details_element.find_elements(By.CSS_SELECTOR, ".trainSubsChild .rail-class")
        availability_elements = train_details_element.find_elements(By.CSS_SELECTOR, ".trainSubsChild .availibilty-info")
        price_elements = train_details_element.find_elements(By.CSS_SELECTOR, ".trainSubsChild .ticket-price")
        
        #Saving links with key as train name and value as train_detail_element
        links[train_name]=train_details_element
        # Iterate over each rail class, availability, and ticket price element and store the information
        for rail_class_element, availability_element, price_element in zip(rail_class_elements, availability_elements, price_elements):
            train_details_string += f"Rail Class: {rail_class_element.text.strip()}\n"
            train_details_string += f"Availability: {availability_element.text.strip()}\n"
            train_details_string += f"Price: {price_element.text.strip()}\n"
            train_details_string += "-" * 50 + "\n"  # Separator between different availability options
    #driver.quit()

    
    # Return the train details string
    if num_of_trains == 0:
        return "No direct trains available between those cities for that date!"
    else:
        print("total number of trains available on this route are : ",num_of_trains)
        #print(train_details_string)
        return [train_details_string,driver,links]



# Streamlit app

def initialize_agent(train_details, origin, destination, travel_date):
    agent = geminichain(mem='y', system_message=f"""1. You are a friendly multi-lingual train ticket booking AI agent named AgentRail and you are an expert at solving user railway queries. 
                        You were created by Xaisr. 2. User has asked for trains traveling from {origin} to {destination} on {travel_date} and you are supposed to give him an explanatory, well-structured and meaningful answer in bullet point format.
                        3. Use below given examples and trains scheduling information to help answer user queries. If no trains are found between {origin} to {destination} , then you can suggest the user to travel via an intermediate station based on your pre-existing knowledge of indian railways.
                        4. Example Rail Class = SL means sleeper class/category, Rail Class "1A"/"2A"/"3A" means first AC, second AC, third AC class/category. Rail Class "CC" means chair car, Rail Class "2S" means second sitting. Rail Class "EC" means executive chair., Rail Class "3E" means AC three tier(economy) 
                        5. Logic: If Availability != AVAILABLE X, where X is any number for a given Rail Class then, confirmed booking can't be currently done for that RAIL Class. Examples below: 
                        6. Example: "Availability : AVAILABLE 10" availability/booking status means 10 tickets are currently available for confirmed reservation/booking. 
                        7. Logic: "Availability : RLWL X" booking/availability status where X is any number means Waitlisted with 17 waiting status, so tickets/seats can't be immediately confirmed/reserved. 
                        8. Logic: "Availability : GNWL X" booking/availability status where X is any number means Waitlisted with 17 waiting status, so tickets/seats can't be immediately confirmed/reserved.
                        9. Example: "TQWL 32", "PQWL 98", "GNWL 125" means there is waitlisting OF 32 AND 24 respectively and tickets can't be immediately confirmed/reserved. 
                        10.Example: "Availability : AVAILABLE 17" booking status means 17 tickets/seats are immediately available for booking/reservation. 
                        11."Departs on : S M T W T F S" implies on which days of the week does this train travel wherein S M T . . mean Sunday, Monday and so on. 
                        12.Try to keep the conversation about railway travel queries only. Your response should be neat, structured and well-formatted for easy readibility. 
                        13.Pay close attention to user query conditions and criteria and then respond. 
                        14.Never give false or made-up information. Give logical and reasoning based answer assisted with relevant train details formatted as bullet/sub-bullet points.
                        15.You are expert in all Indian languages and responds with accurate details but also in the same language as the user query. 
                        16.You have the ability to book train tickets via routing users to booking websites. If the user has expressed his desire to book/reserve a certain trains's ticket. 
                        You will be having 2 pieces of information before proceeding to book ticket : Train Name and Rail Class, so confirm them with user before moving to next step. Please give this preceding information to user to assist him so that he can provide your with his details.
                        Then show all details for the train being booked and preferred rail class and ask for a final booking confirmation again in this format as shown below : 
                        Train Element Number :
                        Train Name :
                        Train Departure Number :
                        Departure Time :
                        Departure Station :
                        Departure Time :
                        Arrival Station :
                        Rail Class :
                        Availability :
                        Price :
                        and if the user again confirms his choice of booking without any changes, then your next response should be exactly like below but filled in with actual values of train element number, rail class and train name at appropriate places : 
                        Booking Selected! Routing you to MMT website | Train Element Number : |Train Name : | Rail Class :
                        17. As you have the ability to book ticktes, so Never say : I am sorry, I can't book a ticket for you at the moment. I can only provide you with train details and schedules.
                        18.Train scheduling information : {train_details}""", temperature=0.1)
    return agent


def main():

    st.title("AgentRail: Your Friendly AIndian-Rail Agent")

    # Sidebar for origin, destination, and travel date
    st.sidebar.header("Enter Travel Details")
    origin = st.sidebar.text_input("Enter your origin city station: ")
    destination = st.sidebar.text_input("Enter your destination city station: ")
    
    # Get current date in yyyymmdd format
    ############################################
    current_date = datetime.now().strftime("%Y%m%d")
    min_date = datetime.now()

    # Calendar for selecting the travel date
    travel_date = st.sidebar.date_input("Enter your travel date:", min_value=min_date)
    ############################################

    if "train_details" not in st.session_state:
        st.session_state.train_details = ""

    if "agent" not in st.session_state:
        st.session_state.agent = None
    
    
    submit_container = st.sidebar.container()
    with submit_container:
        if st.sidebar.button("Submit"):
            with st.spinner("Fetching Train Details ..."):

                with st.empty():
                    try:
                        train_details, driver, links = fetch_train_details(origin, destination, travel_date.strftime("%Y%m%d"))
                        st.session_state.train_details = train_details
                        st.session_state.driver = driver
                        st.session_state.links=links
                        #st.session_state.train_details = fetch_train_details(origin, destination, travel_date.strftime("%Y%m%d"))
                        st.session_state.agent = initialize_agent(st.session_state.train_details, origin, destination, travel_date)
                    except:
                        st.write("Unfortunately, No direct train routes are available for this choice!")
                        print("No direct train routes available!")
                
        
        ### side bar for instructions
        st.sidebar.markdown("---")
        st.sidebar.markdown("## Instructions")
        st.sidebar.write("- Make sure you have Firefox browser installed.")
        st.sidebar.write("- Make sure you are logged into your MakeMyTrip account.")
        st.sidebar.write("- Do not disturb the Firefox browser automation.")
        

    # Main area for user query and agent response
    user_query = st.text_input("_",label_visibility='hidden',value="", key="user_query", placeholder="Enter your query for AgentRail")
    
    # Clickable pre-defined user questions
    if st.button("Show me details of top 3 trains in your data"):
        user_query = "Show me details of top 3 trains in your data"
    if st.button("Show trains with immediate confirmation available for an AC rail class"):
        user_query = "Show trains with immediate confirmation available for an AC rail class"
    if st.button("I am in a hurry, show me train with shortest duration of journey"):
        user_query = "I am in a hurry, show me train with shortest duartion of journey"
    
    
    if user_query and st.session_state.agent:
        with st.empty():
            thinking_placeholder = st.empty()
            typing_placeholder = st.empty()
            thinking_placeholder.write("AgentRail is thinking ...")
            while True:
                dots = ""
                for i in range(3):
                    time.sleep(0.5)
                    dots += "."
                    thinking_placeholder.write("AgentRail is thinking" + dots)
                
                time.sleep(0.1)
                thinking_placeholder.write("AgentRail is thinking ...")
                
                if st.session_state.agent.get_response(user_query) != '':
                    break
            
            time.sleep(0.1)
            #typing_placeholder.write("AgentRail is typing . . .")
            time.sleep(1)

            agent_response = st.session_state.agent.get_response(user_query)
        

        # typing_placeholder=st.empty()
        typing_placeholder.write("AgentRail is typing ...")
        time.sleep(0.1)
        agent_response_placeholder = st.empty()
        typed_response = ""
        for char in agent_response:
            typed_response += char
            agent_response_placeholder.markdown(f"<p style='font-size:15px;'>AgentRail: {typed_response}</p>", unsafe_allow_html=True)
            #agent_response_placeholder.text("AgentRail: " + typed_response)
            #agent_response_placeholder.write(f"<p style='font-size:15px;'>AgentRail: {typed_response}</p>", unsafe_allow_html=True)
            time.sleep(0.001)
        
        ###########################################################################################   

        if "Booking Selected" in agent_response or "Booking Confirmed" in agent_response:
        # Your code here

           # os.environ.pop('MOZ_HEADLESS')

            print("Below is Agent Response : ")
            print(agent_response)

            # Extract train element number using regex
            train_element_number_match = re.search(r"Train Element Number: (\d+)", agent_response)
            if train_element_number_match:
                train_element_number = int(train_element_number_match.group(1))
                st.session_state.booked_train_element_number = train_element_number
            else:
                print("Could not find train element number in the agent response.")

            # Extract rail class using regex
            rail_class_match = re.search(r"Rail Class: (\w+)", agent_response)
            if rail_class_match:
                rail_class = rail_class_match.group(1)
                st.session_state.booked_rail_class = rail_class
            else:
                print("Could not find rail class in the agent response.")
            
            # Extract train name using Regex
            train_name_match = re.search(r"Train Name: \s*(.*?)\s*\|", agent_response)
            if train_name_match:
                train_name = train_name_match.group(1)
                st.session_state.booked_train_name = train_name
            else:
                print("Could not find train name in the agent response.")
            
            #os.environ.pop('MOZ_HEADLESS')
            # Making sure that relevant elements are available for printing : 
            if "booked_train_name" in st.session_state and "booked_rail_class" in st.session_state:
                print(f"Your reserved train name is: {st.session_state.booked_train_name}")
                print(f"Your reserved train element number is: {st.session_state.booked_train_element_number}")
                print(f"Your reserved rail class is: {st.session_state.booked_rail_class}")
                print("This Train element's link is : ",st.session_state.links[train_name])
           
            #######################################################################################################################################################################################
           
            # This code snip is about booking the train by clicking on the relevant rail class element:
            if "booked_train_name" in st.session_state and "booked_rail_class" in st.session_state:
                
                #train_number = st.session_state.booked_train_element_number+1  # Replace with the desired train number
                #rail_class_number = 1  # Replace with the desired rail-class number

                # CSS selector for the desired train name
                #train_name_selector = f"div.single-train-detail:nth-child({train_number}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)"

                # CSS selector for the desired rail-class element
                #rail_class_selector = f"div.single-train-detail:nth-child({train_number}) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child({rail_class_number})"

                # Find the train name element
                #train_name_element = st.session_state.driver.find_element(By.CSS_SELECTOR, train_name_selector)

                # Find the desired rail-class element
                #rail_class_element = st.session_state.driver.find_element(By.CSS_SELECTOR, rail_class_selector)

                # Click on the rail-class element
                #rail_class_element.click()
                
                rail_class_elements = st.session_state.links[st.session_state.booked_train_name].find_elements(By.CSS_SELECTOR, ".trainSubsChild .rail-class")
                # Assume rail_class_value contains the desired value "1A"
                for rail_class_element in rail_class_elements:
                   
                    if rail_class_element.text.strip() == st.session_state.booked_rail_class:
                        rail_class_element.click()
                        break  # Exit the loop once the desired element is clicked
                
                try:
                # Wait for the "Change of Station" element to be clickable (optional)
                    ele = WebDriverWait(st.session_state.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.latoBold")))
    
                # Once the element is clickable, click on it
                    ele.click()

                except Exception as e:
                # Ignore any exceptions and continue execution
                    pass



if __name__ == "__main__":
    main()




