use std::collections::HashMap;

pub fn brackets_are_balanced(string: &str) -> bool {
    Brackets::from(string).are_balanced()
}

struct Brackets {
    raw_brackets: Vec<char>,
    pairs: MatchingBrackets,
}

impl From<&str> for Brackets {
    fn from(i: &str) -> Self {
        Brackets::new(i, None)
    }
}

impl Brackets {
    fn new(s: &str, pairs: Option<Vec<(char, char)>>) -> Self {
        let p = match pairs {
            Some(x) => MatchingBrackets::from(x),
            None => MatchingBrackets::from(vec![('[', ']'), ('{', '}'), ('(', ')')]),
        };

        Brackets {
            raw_brackets: s.chars().filter(|c| p.contains(c)).collect::<Vec<char>>(),
            pairs: p,
        }
    }

    fn are_balanced(&self) -> bool {
        let mut unclosed: Vec<char> = Vec::new();

        for &bracket in self.raw_brackets.iter() {
            if let Some(last_unclosed) = unclosed.pop() {
                unclosed.extend(self.pairs.unmatched(last_unclosed, bracket));
            } else {
                unclosed.push(bracket);
            }
        }

        unclosed.is_empty()
    }
}

struct MatchingBrackets {
    collection: HashMap<char, char>,
}

impl From<Vec<(char, char)>> for MatchingBrackets {
    fn from(v: Vec<(char, char)>) -> Self {
        MatchingBrackets {
            collection: v.into_iter().collect::<HashMap<char, char>>(),
        }
    }
}

impl MatchingBrackets {
    fn contains(&self, other: &char) -> bool {
        self.collection
            .iter()
            .any(|(k, v)| k == other || v == other)
    }

    fn closer_for(&self, k: &char) -> Option<&char> {
        self.collection.get(k)
    }

    fn closed_by(&self, l: char, r: char) -> bool {
        match self.closer_for(&l) {
            Some(&x) => r == x,
            None => false,
        }
    }

    fn unmatched(&self, open: char, potential_close: char) -> Vec<char> {
        let mut ret: Vec<char> = Vec::new();

        if !self.closed_by(open, potential_close) {
            ret.push(open);
            ret.push(potential_close);
        }

        ret
    }
}


fn main() {
    let inputs: Vec<&str> = vec!["[]", "", "[[", "}{", "{ }", "{[])", "{[]}", "{}[]", "{[)][]}", "([{])", "[({]})", "[({}])", "[]]", ")()", "{)()", "(((185 + 223.85) * 15) - 543)/2"];
    let mut out: Vec<String> = Vec::new();
    for &x in inputs.iter() {
        out.push(if brackets_are_balanced(x) { "true".to_string() } else { "false".to_string() });
    }
    println!("{{\"out\": [{}]}}", out.join(","));
}
