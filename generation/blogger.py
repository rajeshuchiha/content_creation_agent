import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def postBlog(text):

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
        

if __name__ == "__main__":
    text = """
    <h1>The Majesty of the Burj Khalifa: A Pinnacle of Human Achievement</h1>\n<p>Standing at an astounding height of 828 meters (2,717 feet), the Burj Khalifa in Dubai is not just the world's tallest building, but also a symbol of human ambition, innovation, and architectural brilliance. This iconic skyscraper dominates the Dubai skyline, drawing millions of visitors annually to marvel at its sheer scale and intricate design.</p>\n<h2>A Visionary Design and Engineering Marvel</h2>\n<p>Designed by Adrian Smith of Skidmore, Owings & Merrill (SOM), the Burj Khalifa's design is inspired by the Hymenocallis flower, featuring a triple-lobed footprint that maximizes views of the Arabian Gulf. Its Y-shaped plan provides an inherently stable configuration for the supertall structure and offers an optimal residential and hotel layout. The building tapers as it rises, with setbacks at different levels, which helps to reduce the effect of wind forces on the structure.</p>\n<p>The construction of the Burj Khalifa was a monumental undertaking, involving over 12,000 workers and utilizing groundbreaking engineering techniques. The foundation alone consists of a massive reinforced concrete mat supported by piles, ensuring its stability in challenging desert conditions. The exterior is clad in reflective glazing, aluminum and textured stainless steel spandrel panels, and vertical stainless steel fin elements, all designed to withstand Dubai's intense summer heat.</p>\n<h2>More Than Just a Building</h2>\n<p>Beyond its record-breaking height, the Burj Khalifa is a mixed-use skyscraper, housing luxury residences, corporate suites, and the Armani Hotel. It boasts several observation decks, including \"At the Top\" on the 124th and 125th floors, and \"At the Top SKY\" on the 148th floor, offering unparalleled panoramic views of Dubai and beyond. The surrounding Downtown Dubai area, with its stunning fountains and vibrant atmosphere, further enhances the Burj Khalifa's appeal as a global landmark.</p>\n<h2>A Global Icon and Tourist Destination</h2>\n<p>Since its inauguration in 2010, the Burj Khalifa has become synonymous with Dubai's rapid growth and futuristic vision. It stands as a testament to what can be achieved with bold ambition and cutting-edge technology. Its presence has significantly boosted Dubai's tourism industry, attracting visitors from all corners of the world eager to experience this architectural wonder firsthand. The Burj Khalifa is not just a building; it is an experience, a statement, and an enduring symbol of human endeavor reaching for the sky.</p>
    """
    postBlog(text)