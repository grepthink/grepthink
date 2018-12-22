Meeting Planner | Design Document
======
Grepthink

Document Version: 1
Edit Date: 28 Oct 18


Goal: build a simple and intuitive tool that allows a team to view overlapping times in their schedules and plan weekly meetings.

#### User Stories

As a user I want

1. to add my weekly schedule after signup.
    - This ensures that every user gets an opportunity to fill out their schedule.
    - It is important to motivate the users to fill out their schedules (incentives: match with a team that you'll work well with, increase the productivity of existing team, some form of gamification)

2. to edit my schedule.
    - Send notification to Project Owner or Scrum mater when a member has updated their schedule.

3. to view my team's collective schedule.
    - ~Explain the purpose of this overlap schedule is to bootstrap the tedious planning stages of group scheduling.~

4. to select preferred blocks in the collective schedule so that popular weekly meeting times are visible to the whole team.



#### Views

- /meeting-planner/ : Main weekly agenda view that will display potential meeting times for a team. Buttons to add/edit user schedule redirects the user to /meeting-planner/edit/ and buttons to vote call API endpoint at /meeting-planner/vote/ that increments the popularity score of whichever meeting block was voted up.


- /meeting-planner/edit/ : Weekly agenda for the user to add/edit busy blocks in their average weekly schedule that can't be used to meet for the project.

- /meeting-planner/vote/ : Endpoint that increments the score of a meeting block. 
