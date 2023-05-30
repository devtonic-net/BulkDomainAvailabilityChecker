import pprint
from eureg import Eureg

eureg = Eureg()

# Example usage. Insert up to 70 keywords
keyword_ideas = ["science blog", "how to make money", "used cars"]

def main():
    results = eureg.get_status(
        domain_names=keyword_ideas,
        preferred_tlds=["ro", "com"],
        return_available_only=False
    )
    pprint.pprint(results)

if __name__ == "__main__":
    main()