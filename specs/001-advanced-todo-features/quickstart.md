# Quickstart Guide: Advanced Todo Features

**Feature**: Advanced Todo Features
**Version**: 2.0
**Date**: 2026-02-09

## Overview

This guide shows you how to use the intermediate and advanced features of the Todo AI Chatbot, including priorities, tags, search, filtering, sorting, due dates, reminders, and recurring tasks.

## Table of Contents

1. [Priority Management](#priority-management)
2. [Tag Organization](#tag-organization)
3. [Search](#search)
4. [Filtering](#filtering)
5. [Sorting](#sorting)
6. [Due Dates and Reminders](#due-dates-and-reminders)
7. [Recurring Tasks](#recurring-tasks)
8. [Using the AI Chatbot](#using-the-ai-chatbot)
9. [Tips and Best Practices](#tips-and-best-practices)

---

## Priority Management

### What are Priorities?

Priorities help you categorize tasks by urgency and importance. There are four priority levels:

- **Low** (Gray badge) - Nice to have, no rush
- **Medium** (Yellow badge) - Normal priority (default)
- **High** (Orange badge) - Important, should be done soon
- **Urgent** (Red badge) - Critical, needs immediate attention

### Setting Priority via UI

1. Click "New Task" or edit an existing task
2. Select priority from the dropdown menu
3. Save the task
4. The task card will display a color-coded priority badge

### Setting Priority via Chat

Simply mention the priority level in your message:

```
"Add urgent task: prepare presentation for tomorrow"
"Add high priority task: review code"
"Make task 5 urgent"
"Change priority of task 3 to low"
```

### Filtering by Priority

1. Click the "Priority" dropdown above the task list
2. Select a priority level (low, medium, high, urgent)
3. Only tasks with that priority will be displayed
4. Click "Clear Filters" to see all tasks again

---

## Tag Organization

### What are Tags?

Tags are labels you can add to tasks to organize them by project, context, or category. Each task can have multiple tags.

### Adding Tags via UI

1. When creating or editing a task, find the "Tags" input field
2. Type a tag name and press Enter
3. The tag appears as a colored chip
4. Add up to 10 tags per task
5. Click the X on a tag chip to remove it

### Adding Tags via Chat

Mention tags in your message:

```
"Add task: review code with tags work and urgent"
"Add task: buy groceries with tag personal"
"Add tag meeting to task 5"
"Remove tag urgent from task 3"
```

### Filtering by Tags

1. Click the "Tags" dropdown above the task list
2. Select one or more tags
3. Only tasks containing ALL selected tags will be displayed
4. Click "Clear Filters" to see all tasks again

### Tag Best Practices

- Use consistent tag names (e.g., "work" not "Work" or "WORK")
- Keep tags short and descriptive
- Common tag categories:
  - Projects: "project-alpha", "website-redesign"
  - Contexts: "work", "personal", "home"
  - Types: "meeting", "email", "call"
  - Status: "urgent", "blocked", "waiting"

---

## Search

### Searching Tasks

1. Type keywords in the search bar above the task list
2. Search looks in both task titles and descriptions
3. Search is case-insensitive
4. Results update as you type

### Search Examples

- Search for "meeting" - finds all tasks with "meeting" in title or description
- Search for "project alpha" - finds tasks containing both words
- Search works with filters active - searches within filtered results

### Search via Chat

```
"Show tasks about meeting"
"Find tasks with presentation"
"Search for grocery tasks"
```

---

## Filtering

### Available Filters

You can filter tasks by:
- **Status**: Pending or Completed
- **Priority**: Low, Medium, High, Urgent
- **Tags**: One or more tags (AND logic)
- **Due Date Range**: Tasks due between two dates

### Using Filters via UI

1. Use the dropdown menus above the task list
2. Select filter criteria
3. Filters combine (AND logic) - task must match all selected filters
4. Click "Clear Filters" to reset

### Filter Examples

**Show only urgent pending tasks:**
- Status: Pending
- Priority: Urgent

**Show work tasks due this week:**
- Tags: work
- Due After: 2026-02-09
- Due Before: 2026-02-16

**Show high priority tasks with specific tags:**
- Priority: High
- Tags: work, urgent

### Filtering via Chat

```
"Show high priority tasks"
"Show pending tasks tagged work"
"Show tasks due this week"
"Show urgent tasks tagged meeting"
```

---

## Sorting

### Available Sort Options

Sort tasks by:
- **Due Date** - Earliest or latest first
- **Priority** - Urgent to low, or low to urgent
- **Created Date** - Newest or oldest first
- **Updated Date** - Recently updated first
- **Title** - Alphabetical order

### Using Sort via UI

1. Click the "Sort by" dropdown above the task list
2. Select a sort field
3. Choose sort order (ascending or descending)
4. Task list reorders immediately

### Sort Examples

**See most urgent tasks first:**
- Sort by: Priority
- Order: Descending (urgent → low)

**See upcoming deadlines:**
- Sort by: Due Date
- Order: Ascending (earliest first)

**See recently created tasks:**
- Sort by: Created Date
- Order: Descending (newest first)

### Sorting via Chat

```
"Show tasks sorted by due date"
"Sort tasks by priority"
"Show tasks by creation date"
```

---

## Due Dates and Reminders

### Setting Due Dates

**Via UI:**
1. When creating or editing a task, find the "Due Date" field
2. Click to open the datetime picker
3. Select date and time
4. Save the task

**Via Chat:**
```
"Add task: meeting tomorrow at 3pm"
"Add task: submit report due Friday at 5pm"
"Set due date for task 5 to next Monday at 9am"
```

### Setting Reminders

**Via UI:**
1. When creating or editing a task, find the "Remind At" field
2. Click to open the datetime picker
3. Select when you want to be reminded
4. Save the task

**Via Chat:**
```
"Add task: meeting tomorrow at 3pm, remind 30 minutes before"
"Add task: call client, remind me in 2 hours"
"Set reminder for task 5 at 2pm today"
```

### How Reminders Work

- Reminders are checked when you load the task list
- When a reminder time is reached, a notification is logged (placeholder for future notification system)
- Each reminder only triggers once
- Reminders can be set for any time, even in the past (will trigger immediately)

### Viewing Due Dates

- Tasks with due dates show a calendar icon and date
- Overdue tasks are highlighted in red
- Due dates display in your local timezone
- Relative times shown for near dates ("Tomorrow", "In 2 hours")

### Filtering by Due Date

**Via UI:**
1. Use "Due After" and "Due Before" date pickers
2. Set a date range
3. Only tasks due within that range are shown

**Via Chat:**
```
"Show tasks due this week"
"Show tasks due today"
"Show overdue tasks"
```

---

## Recurring Tasks

### What are Recurring Tasks?

Recurring tasks automatically create a new task when you complete them. Perfect for routine activities like daily standups, weekly reports, or monthly reviews.

### Creating Recurring Tasks

**Via UI:**
1. When creating a task, find the "Recurrence" dropdown
2. Select a pattern:
   - **Daily** - Repeats every day
   - **Weekly** - Repeats every week
   - **Monthly** - Repeats every month
3. Set a due date (required for recurring tasks)
4. Save the task

**Via Chat:**
```
"Add task: team standup, repeat every day at 9am"
"Add task: weekly report, repeat every Friday at 5pm"
"Add task: monthly review, repeat every 1st of the month"
"Make task 5 repeat every Monday"
```

### How Recurring Tasks Work

1. You create a recurring task with a due date and recurrence pattern
2. When you mark the task as complete, the system:
   - Marks the original task as completed
   - Automatically creates a new task with the next due date
   - The new task inherits: title, description, priority, tags, recurrence pattern
3. The cycle continues each time you complete the task

### Recurring Task Examples

**Daily standup:**
- Title: "Team standup meeting"
- Due Date: Tomorrow at 9:00 AM
- Recurrence: Daily
- Result: New task created every day at 9:00 AM

**Weekly report:**
- Title: "Submit weekly status report"
- Due Date: Next Friday at 5:00 PM
- Recurrence: Weekly
- Result: New task created every Friday at 5:00 PM

**Monthly review:**
- Title: "Monthly performance review"
- Due Date: March 1st at 10:00 AM
- Recurrence: Monthly
- Result: New task created on the 1st of each month

### Stopping Recurring Tasks

**Via UI:**
1. Edit the recurring task
2. Remove the recurrence pattern (set to "None")
3. Save the task
4. When you complete it, no new task will be created

**Via Chat:**
```
"Stop task 5 from repeating"
"Remove recurrence from task 3"
```

---

## Using the AI Chatbot

### Natural Language Commands

The AI chatbot understands natural language for all features. You can combine multiple features in one command:

**Complex Examples:**

```
"Add urgent task: prepare presentation with tags work and meeting due tomorrow at 2pm remind 1 hour before"

"Add task: grocery shopping with tags personal due Saturday at 10am repeat every week"

"Show high priority tasks tagged work due this week sorted by due date"

"Make task 5 urgent, add tag important, and set due date to Friday"
```

### Chatbot Capabilities

The chatbot can:
- ✅ Create tasks with all features (priority, tags, due dates, reminders, recurrence)
- ✅ Update existing tasks
- ✅ Search and filter tasks
- ✅ Complete and delete tasks
- ✅ Show your user profile
- ✅ Understand English and Urdu commands

### Chatbot Tips

1. **Be specific**: "Add urgent task: meeting" is better than "urgent meeting"
2. **Use natural language**: "tomorrow at 3pm" works, no need for exact formats
3. **Combine features**: Include priority, tags, dates in one command
4. **Ask for help**: "Show me my urgent tasks" or "What tasks are due today?"

### Example Conversations

**Creating a complex task:**
```
You: Add urgent task: client presentation with tags work and important due Friday at 2pm remind Thursday at 5pm

Bot: ✓ Task created: "client presentation"
     Priority: urgent
     Tags: work, important
     Due: Friday, Feb 14 at 2:00 PM
     Reminder: Thursday, Feb 13 at 5:00 PM
```

**Finding tasks:**
```
You: Show high priority tasks tagged work

Bot: Found 3 high priority tasks with tag "work":
     1. Client presentation (due Friday)
     2. Code review (due tomorrow)
     3. Team meeting (due today)
```

**Managing recurring tasks:**
```
You: Add task: daily standup repeat every day at 9am

Bot: ✓ Recurring task created: "daily standup"
     Recurrence: Daily at 9:00 AM
     Next occurrence: Tomorrow at 9:00 AM
```

---

## Tips and Best Practices

### Priority Management

- Use **Urgent** sparingly - if everything is urgent, nothing is
- Review and adjust priorities regularly
- Default to **Medium** for most tasks
- Use **High** for important deadlines
- Use **Low** for nice-to-have items

### Tag Organization

- Create a consistent tag system:
  - Projects: "project-name"
  - Contexts: "work", "personal", "home"
  - Types: "meeting", "email", "call"
- Don't over-tag - 2-3 tags per task is usually enough
- Review and consolidate tags periodically

### Search and Filter

- Use search for quick lookups
- Use filters for focused work sessions
- Combine filters for powerful queries
- Save common filter combinations as mental shortcuts

### Due Dates and Reminders

- Set realistic due dates
- Use reminders for time-sensitive tasks
- Set reminders with enough lead time (30 min - 1 hour before)
- Review overdue tasks regularly

### Recurring Tasks

- Perfect for:
  - Daily routines (standup, exercise, review)
  - Weekly tasks (reports, meetings, planning)
  - Monthly tasks (reviews, billing, maintenance)
- Not ideal for:
  - One-time projects
  - Tasks with variable schedules
  - Tasks that might be skipped

### Workflow Suggestions

**Morning Routine:**
1. Check overdue tasks (filter: status=pending, due_before=today)
2. Review today's tasks (filter: due_date=today, sort by priority)
3. Set priorities for new tasks

**Weekly Planning:**
1. Review completed tasks from last week
2. Check upcoming tasks (filter: due_after=today, due_before=next week)
3. Adjust priorities and due dates as needed

**Project Focus:**
1. Filter by project tag (e.g., tags=project-alpha)
2. Sort by due date or priority
3. Work through tasks systematically

---

## Troubleshooting

### Task not showing up?
- Check if filters are active - click "Clear Filters"
- Check if search is active - clear the search bar
- Verify the task wasn't accidentally deleted

### Reminder didn't trigger?
- Reminders trigger when you load the task list
- Check the console log for reminder messages
- Verify remind_at time is in the past

### Recurring task didn't create next occurrence?
- Verify the task has a recurrence pattern set
- Check that the task was marked as completed (not just updated)
- Verify due_date is set (required for recurring tasks)

### Chatbot not understanding commands?
- Be more specific with your request
- Use simpler language
- Try breaking complex commands into smaller steps
- Check that you're using supported features

---

## Getting Help

- **In-app help**: Type "help" in the chatbot
- **Feature questions**: Ask the chatbot "How do I [feature]?"
- **Bug reports**: Contact support with details and screenshots

---

**Ready to get started?** Try creating your first advanced task:

```
"Add high priority task: complete quickstart guide with tags documentation and tutorial due today at 5pm"
```

Happy task managing! 🎯
