import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    # itertools.combinations(s, r) returns an iterable that produces combinates of elements in s of length r
    # itertools.chain(a, b) unpacks elements in a and b, but if a has nested list c, c itself retuns as an iterable
    # itertools.chain.from_iterable(a, b), unpacks elements in a and b, even if a has nested list c, c is unpacked as well, each element of c is separately returned. 
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]
    

def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # people, dict, person - monther/father, trait
    # one_gene: set of people with one copy of the gene
    # two_genes:
    # None, no copy:
    # have_trait/No trait
    no_gene = sorted(set(people) - one_gene - two_genes)
    p_current = {}
    for person in people:
        if people[person]["mother"] is None and people[person]["father"] is None:
            if person in no_gene:
                p_current[person] = PROBS["gene"][0] * (
                    PROBS["trait"][0][True] * int(person in have_trait) + 
                    PROBS["trait"][0][False] * (1 - int(person in have_trait)))
            elif person in one_gene:
                p_current[person] = PROBS["gene"][1] * (
                    PROBS["trait"][1][True] * int(person in have_trait) + 
                    PROBS["trait"][1][False] * (1 - int(person in have_trait)))
            else:
                p_current[person] = PROBS["gene"][2] * (
                    PROBS["trait"][2][True] * int(person in have_trait) + 
                    PROBS["trait"][2][False] * (1 - int(person in have_trait)))
        else:        
            if person in no_gene:
                if people[person]["mother"] in no_gene:
                    p_current[person] = (1 - PROBS["mutation"])
                elif people[person]["mother"] in one_gene:
                    # for this case, inherit no copy and no mutation, 0.5*(1-p(mutation))
                    # or inherit one copy and mutation, 0.5*p(mutation)
                    # Together, it is 0.5
                    p_current[person] = 0.5
                else: 
                    p_current[person] = PROBS["mutation"]
                
                if people[person]["father"] in no_gene:
                    p_current[person] *= (1 - PROBS["mutation"])
                elif people[person]["father"] in one_gene:
                    p_current[person] *= 0.5
                else:
                    p_current[person] *= PROBS["mutation"] 

                # combine with the probability of having traits or not
                p_current[person] *= (
                        PROBS["trait"][0][True] * int(person in have_trait) + 
                        PROBS["trait"][0][False] * (1 - int(person in have_trait)))
                
            if person in one_gene:
                if people[person]["mother"] in no_gene and people[person]["father"] in no_gene:
                    p_current[person] = PROBS["mutation"] * (1 - PROBS["mutation"]) * 2
                elif people[person]["mother"] in no_gene and people[person]["father"] in one_gene:
                    p_current[person] = PROBS["mutation"] * 0.5 * (1 - PROBS["mutation"]) + (
                        (1 - PROBS["mutation"]) * 0.5)
                elif people[person]["mother"] in no_gene and people[person]["father"] in two_genes:
                    p_current[person] = PROBS["mutation"] * PROBS["mutation"] + (
                        (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]))

                elif people[person]["mother"] in one_gene and people[person]["father"] in no_gene:
                    p_current[person] = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
                elif people[person]["mother"] in one_gene and people[person]["father"] in one_gene:
                    p_current[person] = 0.5 * 0.5 * 2
                elif people[person]["mother"] in one_gene and people[person]["father"] in two_genes:
                    p_current[person] = 0.5 * PROBS["mutation"] + 0.5 * (1 - PROBS["mutation"])

                elif people[person]["mother"] in two_genes and people[person]["father"] in no_gene:
                    p_current[person] = (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + (
                        PROBS["mutation"] * PROBS["mutation"])
                elif people[person]["mother"] in two_genes and people[person]["father"] in one_gene:
                    p_current[person] = (1 - PROBS["mutation"]) * 0.5 + PROBS["mutation"] * 0.5
                else:
                    p_current[person] = PROBS["mutation"] * PROBS["mutation"]
                
                p_current[person] *= (
                        PROBS["trait"][1][True] * int(person in have_trait) + 
                        PROBS["trait"][1][False] * (1 - int(person in have_trait)))


            if person in two_genes:
                if people[person]["mother"] in no_gene:
                    p_current[person] = PROBS["mutation"]
                elif people[person]["mother"] in one_gene:
                    p_current[person] = 0.5
                else: 
                    p_current[person] = 1 - PROBS["mutation"]

                if people[person]["father"] in no_gene:
                    p_current[person] *= PROBS["mutation"]
                elif people[person]["father"] in one_gene:
                    p_current[person] *= 0.5
                else:
                    p_current[person] *= 1 - PROBS["mutation"] 
                p_current[person] *= (
                        PROBS["trait"][2][True] * int(person in have_trait) + 
                        PROBS["trait"][2][False] * (1 - int(person in have_trait)))

    joint_p = 1
    for person in p_current:
        joint_p *= p_current[person]
    return joint_p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        p_gene = sum(probabilities[person]["gene"].values())
        p_trait = sum(probabilities[person]["trait"].values())
        if p_gene != 0:
            for g in probabilities[person]["gene"]:
                probabilities[person]["gene"][g] /= p_gene
        if p_trait != 0:
            for t in probabilities[person]["trait"]:
                probabilities[person]["trait"][t] /= p_trait



if __name__ == "__main__":
    main()
