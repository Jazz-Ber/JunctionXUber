**Application Description:**

- Simulation of a potential feature that can help Uber drivers find busy areas to decrease time until a new request, based on a set of categories dependent on time and day, which creates clusters of busy and open venues. Can also find close by parking garages to take a break.
  - Find Busy Area: Showcases close by busy clusters for the user to select one to route to.
  - Find Idle Place: Showcases close by busy clusters for the user to select one and routes to a close by parking garage so that after their break the driver is already in a busy area.
  - User can insert a custom location to simulate the features in different locations.

**Limitations:**

- All data is received and displayed using free APIs and libraries and may not be perfect or limited in some countries.
- The map view may need a bit to load sometimes, if there is a slow internet connection.

**How to Run:**

- Python needs to be installed to run this program

1. Insert your API key in configs/conifg.json in place of "INSERT HERE"
2. Run install_dependencies.py to install the required pip libraries
3. Run main.py to open the application

**How to get API Key:**

1. Go to www.foursquare.com/developers/home
2. Create an account
3. Create a new project
4. Click "Generate API Key"
5. Click "Generate Service API Key"
6. Copy it into the confi.json file
