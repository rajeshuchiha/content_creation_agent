import os
from google.auth.transport import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

text = """ 
<!DOCTYPE html>
<html>
<head>
    <title>Tyrannosaurus Rex: The Reigning King of Strength and Size</title>
</head>
<body>
    <h1>Tyrannosaurus Rex: The Reigning King of Strength and Size</h1>
    <p>When we think of raw power and imposing presence, few creatures, past or present, can rival the legendary Tyrannosaurus Rex. This iconic dinosaur, whose name means "tyrant lizard king," truly lived up to its moniker, dominating the late Cretaceous period with an awe-inspiring combination of immense size and unparalleled strength.</p>

    <h2>A Colossus Among Dinosaurs</h2>
    <p>The sheer scale of the T-Rex is difficult to comprehend. Imagine a creature that could stretch up to 40 feet (12 meters) long, stand 20 feet (6 meters) tall, and weigh anywhere from 8 to 14 tons. To put that into perspective, an adult male African elephant, one of the largest land animals alive today, typically weighs around 6 tons. The T-Rex wasn't just big; it was a mobile fortress of muscle and bone.</p>

    <h2>Unmatched Predatory Power</h2>
    <p>But size was only one part of its terrifying arsenal. The true measure of the T-Rex's might lay in its incredible strength, particularly its bite force. Scientists estimate that the Tyrannosaurus Rex possessed the strongest bite of any known terrestrial animal, capable of delivering a crushing force of up to 12,800 pounds per square inch (psi). This is enough to shatter bones and tear through flesh with devastating efficiency, far exceeding the bite force of any modern predator.</p>
    <ul>
        <li><strong>Modern Bears:</strong> A grizzly bear's bite force is around 1,200 psi.</li>
        <li><strong>Large Crocodiles:</strong> The saltwater crocodile, known for its powerful jaws, can exert about 3,700 psi.</li>
        <li><strong>Lions and Tigers:</strong> These apex predators of today have bite forces ranging from 650-1,000 psi.</li>
    </ul>
    <p>None come close to the bone-crushing power of the T-Rex. Its robust skull, massive jaw muscles, and serrated, banana-sized teeth were perfectly engineered for dismembering prey, making it an undisputed apex predator.</p>

    <h2>Beyond the Bite: A Powerful Hunter</h2>
    <p>Beyond its fearsome jaws, the T-Rex's entire physique was built for power. Its massive hind legs, though seemingly heavy, were muscular and capable of propelling its enormous body at considerable speeds for short bursts, making it an effective pursuit predator. The small, two-fingered forelimbs, while a subject of much debate, were likely powerful enough for gripping or stabilizing prey during a kill.</p>

    <h2>Conclusion: A Legacy of Dominance</h2>
    <p>When compared to the strongest species of today, the Tyrannosaurus Rex stands as a testament to prehistoric might. While modern animals like elephants possess immense strength for their size, and predators like polar bears and crocodiles are formidable, none combine the sheer scale, bone-shattering bite force, and predatory prowess that defined the T-Rex. It remains, in every sense of the word, the ultimate king of the terrestrial food chain, a symbol of raw, untamed power that continues to captivate our imaginations.</p>
</body>
</html>

"""
creds = None

if os.path.exists("tokens.json"):
    creds = Credentials.from_authorized_user_file('tokens.json', scopes=["https://www.googleapis.com/auth/blogger"])
    
if not creds or not creds.valid:
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=["https://www.googleapis.com/auth/blogger"]
        )

        creds = flow.run_local_server(port=0)

        with open("tokens.json", "w") as file:
            file.write(creds.to_json())

try:
    service = build("blogger", "v3", credentials=creds)

    blog_id = "3115491518418580833"

    post_body = {
        "kind": "blogger#post",
        "blog":{
            "id": blog_id
        },
        "title": "Test Post",
        "content": text,
        "labels": ['test', 'first']
    }
    new_post = service.posts().insert(blogId = blog_id, body=post_body, isDraft=False).execute()

    print(f"The new post is at url: {new_post['url']}")
    
except HttpError as error:
    print(f"An error Occurred: {error}")