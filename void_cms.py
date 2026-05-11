import os
import yaml
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, ListItem, ListView, Input, Label, RichLog
from textual.screen import Screen
from rich.markdown import Markdown
from rich.panel import Panel

SITE_ROOT = os.getcwd()

class PostItem(ListItem):
    def __init__(self, filename, title):
        super().__init__()
        self.filename = filename
        self.title = title

    def compose(self) -> ComposeResult:
        yield Label(f"📄 {self.title} [dim]({self.filename})[/dim]")

class ContentScreen(Screen):
    """Screen to list and select content."""
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("--- SELECT CONTENT TO EDIT ---", id="title"),
            ListView(id="post-list"),
            id="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self):
        list_view = self.query_one("#post-list")
        list_view.clear()
        
        # Look for markdown files in root and subfolders
        for root, dirs, files in os.walk(SITE_ROOT):
            if "_site" in root or ".git" in root: continue
            for file in files:
                if file.endswith(".md"):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, SITE_ROOT)
                    with open(path, 'r') as f:
                        content = f.read()
                        try:
                            # Basic title extraction
                            if "title:" in content:
                                title = content.split("title:")[1].split("\n")[0].strip()
                            else:
                                title = file
                        except:
                            title = file
                    list_view.append(PostItem(rel_path, title))

class NewPostScreen(Screen):
    """Screen to create a new post."""
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("--- CREATE NEW CONTENT ---", id="title"),
            Vertical(
                Label("Title:"),
                Input(placeholder="My New Note", id="input-title"),
                Label("Section (math, cs, cool-stuff):"),
                Input(placeholder="math", id="input-section"),
                Label("Nav Order:"),
                Input(placeholder="10", id="input-order"),
                Button("GENERATE CONTENT", variant="success", id="btn-create"),
            ),
            id="main-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-create":
            title = self.query_one("#input-title").value
            section = self.query_one("#input-section").value
            order = self.query_one("#input-order").value
            
            if not title or not section: return

            filename = f"{title.lower().replace(' ', '-')}.md"
            target_dir = os.path.join(SITE_ROOT, section)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            filepath = os.path.join(target_dir, filename)
            
            front_matter = {
                "layout": "default",
                "title": title,
                "nav_order": int(order) if order.isdigit() else 10
            }
            
            with open(filepath, 'w') as f:
                f.write("---\n")
                yaml.dump(front_matter, f)
                f.write("---\n\n")
                f.write(f"# {title}\n\nStart writing here...")
            
            self.app.push_screen("deploy")

class DeployScreen(Screen):
    """Screen to deploy changes."""
    message = "Changes ready for deployment"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("--- DEPLOYMENT HUB ---", id="title"),
            Static(self.message, id="status-msg"),
            RichLog(id="git-log", highlight=True),
            Horizontal(
                Button("GIT PUSH", variant="primary", id="btn-push"),
                Button("BACK TO DASHBOARD", id="btn-back"),
            ),
            id="main-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-push":
            log = self.query_one(RichLog)
            log.write("🚀 Starting deployment...")
            os.system("git add .")
            os.system('git commit -m "Content update via VOID-CMS"')
            os.system("git push origin main")
            log.write("✅ Pushed to GitHub!")
        elif event.button.id == "btn-back":
            self.app.pop_screen()

class VoidCMS(App):
    CSS = """
    Screen {
        background: #0a0a0a;
    }
    #main-container {
        padding: 2 4;
        border: solid #333333;
        margin: 2 4;
    }
    #title {
        text-align: center;
        width: 100%;
        color: #fff;
        margin-bottom: 2;
        text-style: bold;
    }
    Label {
        color: #888;
        margin-top: 1;
    }
    Input {
        background: #111;
        border: solid #222222;
        color: #fff;
    }
    Button {
        margin-top: 2;
        width: 100%;
    }
    #status-msg {
        background: #1a1a1a;
        padding: 1 2;
        border: solid #333333;
        margin-bottom: 2;
        color: #0f0;
    }
    #git-log {
        height: 10;
        background: #000;
        border: solid #222222;
        margin-bottom: 2;
    }
    ListView {
        background: #111;
        border: solid #222222;
        height: 15;
    }
    ListItem {
        padding: 1;
    }
    ListItem:hover {
        background: #222;
    }
    """
    
    BINDINGS = [
        ("n", "push_screen('new')", "New Content"),
        ("l", "push_screen('list')", "List Content"),
        ("d", "push_screen('deploy')", "Deploy"),
        ("q", "quit", "Quit"),
    ]

    SCREENS = {
        "list": ContentScreen,
        "new": NewPostScreen,
        "deploy": DeployScreen,
    }

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("V O I D - C M S", id="title"),
            Static(Panel(
                "[bold white]Welcome to the Void.[/]\n\n"
                "[cyan]N[/cyan] - Create New Content\n"
                "[cyan]L[/cyan] - List & Edit Content\n"
                "[cyan]D[/cyan] - Deploy to GitHub\n"
                "[cyan]Q[/cyan] - Exit CMS",
                title="DASHBOARD",
                border_style="#333333"
            )),
            id="main-container"
        )
        yield Footer()

if __name__ == "__main__":
    app = VoidCMS()
    app.run()
