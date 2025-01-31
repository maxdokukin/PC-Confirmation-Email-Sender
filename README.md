# Automated Tutoring Email & Calendar Event Script

Part of my tutoring job is to send out emails to students once they book an appointment with me. That is usually a simple email with an introduction and session topic clarification request.  

Of course, I could do it myself. But that's no fun. So I copy-paste email text to this Python script. What it does is extract data from it, and then compose and send an email to the student. Moreover, it pops a nice event in my calendar with all the necessary data.  

I spent around 2 hours on development. And it would have definitely taken me less time to do it by hand. But there is no fun there.  

The way it works (on Mac) is there is **Automator** app that provides quick run functionality from `cmd+space` search bar. From there, Automator launches `run_script.sh`. That script opens the Terminal app and runs `send_pc_email.sh`. Then the user should paste the raw email text in the terminal window, and type the email, and enjoy saving 2 minutes of life. Also, automation eliminates human mistakes and confusion with dates.  

Anyways, fun little project that makes life a little more automatic. Nice.