import math
import nltk
import os, sys, string


FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)
  

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)
    
    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    txt_dict = {}
    for file in os.listdir(directory):
        f_path = os.path.join(directory, file)
        with open(f_path) as f:
            txt_dict[file] = f.read()
    return txt_dict

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokens = nltk.tokenize.word_tokenize(document)
    words = []
    for w in tokens: 
        w_lower = w.lower()
        if w_lower in string.punctuation or w_lower in nltk.corpus.stopwords.words("english"):
            continue
        else:
            words.append(w_lower)
    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    words_docs = {}
    words_idfs = {}
    num_docs = len(documents)
    for document in documents:
        for word in documents[document]:
            if word not in words_docs:
                words_docs[word] = []
            if document not in words_docs[word]:
                words_docs[word].append(document)
    for word in words_docs:
        words_idfs[word] = math.log(num_docs/len(words_docs[word]))
    return words_idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs_files = {}
    for file in files:
        tf_idfs = {}
        for word in query:
            tf_idfs[word] = files[file].count(word)
        for key in tf_idfs:
            tf_idfs[key] *= idfs[key]
        tf_idfs_files[file] = sum(tf_idfs.values())
    return sorted(tf_idfs_files, key=tf_idfs_files.get, reverse = True)[:n]



def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    idfs_sent = {}
    for sentence in sentences:
        idfs_sent[sentence] = {}
        idfs_sent[sentence]["density"] = 0
        idfs_sent[sentence]["idf"] = 0
        # query is a set, no duplicates
        for word in query:
            if word in sentences[sentence]:
                idfs_sent[sentence]["density"] += sentences[sentence].count(word)
                idfs_sent[sentence]["idf"] += idfs[word]
        idfs_sent[sentence]["density"] /= len(sentences[sentence])
    return sorted(idfs_sent, key=lambda x: (idfs_sent[x]["idf"], idfs_sent[x]["density"]), reverse=True)[:n]
    

if __name__ == "__main__":
    main()
