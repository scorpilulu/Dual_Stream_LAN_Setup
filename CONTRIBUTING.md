# Contributing to LAN Screen Streamer 🤝

First off, thank you for considering contributing to LAN Screen Streamer! It's people like you that make this tool better for everyone.

## 🌟 How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check existing issues to avoid duplicates.

When you create a bug report, please include:
- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs what actually happened
- **Screenshots** if applicable
- **System information** (Windows version, Python version)
- **Error messages** or logs

### Suggesting Features 💡

We love new ideas! When suggesting features:
- **Check existing issues** first
- **Explain the problem** your feature would solve
- **Describe the solution** you'd like
- **Consider alternatives** you've thought about

### Code Contributions 💻

#### First Time Contributing?

1. Fork the repo
2. Clone your fork: `git clone https://github.com/your-username/LAN-Streamer-Project.git`
3. Create a branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Test thoroughly
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

#### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/LAN-Streamer-Project.git
cd LAN-Streamer-Project

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

#### Code Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused
- Write docstrings for all functions

Example:
```python
def calculate_frame_rate(total_frames: int, duration: float) -> float:
    """
    Calculate the frame rate from total frames and duration.
    
    Args:
        total_frames: Number of frames processed
        duration: Time taken in seconds
        
    Returns:
        Frame rate as frames per second
    """
    if duration <= 0:
        return 0.0
    return total_frames / duration
```

### Documentation 📚

Documentation improvements are always welcome! This includes:
- README updates
- Code comments
- Wiki pages
- Tutorial videos or GIFs

## 📋 Pull Request Process

1. **Update README.md** if you've changed functionality
2. **Add tests** for new features
3. **Update requirements.txt** if you've added dependencies
4. **Ensure all tests pass**
5. **Get approval** from at least one maintainer

### PR Checklist

- [ ] My code follows the project's style guidelines
- [ ] I've performed a self-review
- [ ] I've commented my code where necessary
- [ ] I've updated the documentation
- [ ] My changes don't break existing functionality
- [ ] I've added tests for my features
- [ ] All tests pass locally

## 🎯 What We're Looking For

### High Priority
- 🐛 Bug fixes
- 🔧 Performance improvements
- 📱 Cross-platform support
- 🔒 Security enhancements

### Good First Issues
Look for issues tagged with `good first issue` - these are perfect for beginners!

### Areas Needing Help
- **Testing**: More test coverage
- **Documentation**: Tutorials and guides
- **UI/UX**: Better user interface
- **Optimization**: Reduce latency and improve quality

## 💬 Communication

### Discord/Discussion
- Be respectful and inclusive
- Help others when you can
- Ask questions - no question is too simple!

### Issue Comments
- Stay on topic
- Be constructive
- Help reproduce bugs

## 🚫 What Not To Do

- Don't submit large PRs without discussion
- Don't change coding style without agreement
- Don't add dependencies without necessity
- Don't commit sensitive information

## 🏆 Recognition

Contributors will be:
- Listed in our README
- Mentioned in release notes
- Given credit in the code

## 📜 Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone.

### Expected Behavior
- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information

## ❓ Questions?

Feel free to:
- Open an issue with the `question` tag
- Start a discussion
- Contact maintainers

## 🙏 Thank You!

Every contribution, no matter how small, helps make LAN Screen Streamer better. We appreciate your time and effort!

---

**Happy Coding!** 🚀
