// Enhanced Quiz Generation with Complete Questions and Answers
function generateQuiz() {
    const questionCount = parseInt(document.getElementById('questionCount').value);
    const difficulty = document.getElementById('difficulty').value;
    
    if (questionCount < 1 || questionCount > 20) {
        alert('Please enter a number between 1 and 20 for questions.');
        return;
    }
    
    if (state.extractedContent.length === 0) {
        alert('No content extracted from document. Please try a different file.');
        return;
    }
    
    state.quizSettings.questionCount = questionCount;
    state.quizSettings.difficulty = difficulty;
    
    generateCompleteQuestions();
    displayQuiz();
}

function generateCompleteQuestions() {
    const questions = [];
    const usedContent = new Set();
    
    // Extract complete, meaningful content
    const definitions = extractCompleteDefinitions();
    const concepts = extractCompleteConcepts();
    const examples = extractCompleteExamples();
    const processes = extractCompleteProcesses();
    const classifications = extractCompleteClassifications();
    
    const allContent = [...definitions, ...concepts, ...examples, ...processes, ...classifications];
    
    // Filter out incomplete or invalid content
    const validContent = allContent.filter(content => 
        content && 
        content.question && 
        content.question.length > 15 &&
        !content.question.includes('""') &&
        !content.question.includes('undefined') &&
        content.options && 
        content.options.length >= 4 &&
        content.options.every(opt => opt && opt.length > 2) &&
        content.correctAnswer &&
        content.correctAnswer.length > 3
    );
    
    for (let i = 0; i < state.quizSettings.questionCount && i < validContent.length; i++) {
        let content;
        let attempts = 0;
        
        do {
            content = validContent[Math.floor(Math.random() * validContent.length)];
            attempts++;
        } while (usedContent.has(content.source) && attempts < validContent.length * 2);
        
        if (attempts >= validContent.length * 2) break;
        
        usedContent.add(content.source);
        
        const question = {
            id: i + 1,
            question: content.question,
            options: shuffleArray(content.options),
            correct: content.options.indexOf(content.correctAnswer),
            explanation: content.explanation,
            page: content.page
        };
        
        // Ensure correct answer is properly set after shuffling
        question.correct = question.options.indexOf(content.correctAnswer);
        
        if (question.correct !== -1) {
            questions.push(question);
        }
    }
    
    state.quiz.questions = questions;
    state.quiz.userAnswers = new Array(questions.length).fill(-1);
}

function extractCompleteDefinitions() {
    const definitions = [];
    const sentences = getAllCompleteSentences();
    
    sentences.forEach(sentence => {
        const text = sentence.text.toLowerCase();
        
        // Look for complete definition patterns
        if ((text.includes('is defined as') || 
             text.includes('refers to') || 
             text.includes('means') ||
             text.includes('can be described as') ||
             (text.includes('is the') && text.includes('of'))) && 
            text.split(' ').length > 10) {
            
            const parts = sentence.text.split(/is defined as|refers to|means|can be described as|is the/i);
            if (parts.length >= 2) {
                const term = extractCompleteTerm(parts[0]);
                const definition = extractCompleteDefinition(parts[1]);
                
                if (term && definition && term.length > 3 && definition.length > 20) {
                    const options = generateCompleteDefinitionOptions(term);
                    
                    if (options.length >= 4 && options.includes(term)) {
                        definitions.push({
                            question: `What is the definition of ${term}?`,
                            options: options,
                            correctAnswer: term,
                            explanation: `${term} is defined as: ${definition}`,
                            page: sentence.page,
                            source: sentence.text,
                            type: 'definition'
                        });
                    }
                }
            }
        }
    });
    
    return definitions;
}

function extractCompleteConcepts() {
    const concepts = [];
    const sentences = getAllCompleteSentences();
    
    sentences.forEach(sentence => {
        const text = sentence.text.toLowerCase();
        
        // Look for complete concept explanations
        if ((text.includes('concept of') ||
             text.includes('principle of') ||
             text.includes('theory of') ||
             text.includes('important in') ||
             text.includes('essential for')) && 
            text.split(' ').length > 12) {
            
            const concept = extractMainConcept(sentence.text);
            if (concept && concept.length > 4) {
                const context = extractConceptContext(sentence.text);
                const options = generateCompleteConceptOptions(concept);
                
                if (options.length >= 4 && options.includes(concept)) {
                    concepts.push({
                        question: `What is the main concept discussed in: "${context}"?`,
                        options: options,
                        correctAnswer: concept,
                        explanation: `The text discusses the concept of ${concept}`,
                        page: sentence.page,
                        source: sentence.text,
                        type: 'concept'
                    });
                }
            }
        }
    });
    
    return concepts;
}

function extractCompleteExamples() {
    const examples = [];
    const sentences = getAllCompleteSentences();
    
    sentences.forEach(sentence => {
        const text = sentence.text.toLowerCase();
        
        // Look for complete examples with clear concepts
        if ((text.includes('for example') ||
             text.includes('for instance') ||
             text.includes('such as') ||
             text.includes('including')) && 
            text.split(' ').length > 15) {
            
            const concept = extractExampleConcept(sentence.text);
            const exampleItems = extractExampleItems(sentence.text);
            
            if (concept && exampleItems.length > 0) {
                const options = generateCompleteExampleOptions(concept);
                
                if (options.length >= 4 && options.includes(concept)) {
                    examples.push({
                        question: `What concept is illustrated by examples like ${exampleItems.join(', ')}?`,
                        options: options,
                        correctAnswer: concept,
                        explanation: `Examples like ${exampleItems.join(', ')} illustrate the concept of ${concept}`,
                        page: sentence.page,
                        source: sentence.text,
                        type: 'example'
                    });
                }
            }
        }
    });
    
    return examples;
}

function extractCompleteProcesses() {
    const processes = [];
    const sentences = getAllCompleteSentences();
    
    sentences.forEach(sentence => {
        const text = sentence.text.toLowerCase();
        
        // Look for complete process descriptions
        if ((text.includes('process of') ||
             text.includes('steps involved') ||
             text.includes('procedure for') ||
             text.includes('method to') ||
             text.includes('technique for')) && 
            text.split(' ').length > 15) {
            
            const process = extractProcessConcept(sentence.text);
            if (process && process.length > 4) {
                const options = generateCompleteProcessOptions(process);
                
                if (options.length >= 4 && options.includes(process)) {
                    processes.push({
                        question: `What process involves the steps described in the document?`,
                        options: options,
                        correctAnswer: process,
                        explanation: `The document describes the process of ${process}`,
                        page: sentence.page,
                        source: sentence.text,
                        type: 'process'
                    });
                }
            }
        }
    });
    
    return processes;
}

function extractCompleteClassifications() {
    const classifications = [];
    const sentences = getAllCompleteSentences();
    
    sentences.forEach(sentence => {
        const text = sentence.text.toLowerCase();
        
        // Look for complete classification systems
        if ((text.includes('classified into') ||
             text.includes('divided into') ||
             text.includes('categorized as') ||
             text.includes('types of') ||
             text.includes('categories of')) && 
            text.split(' ').length > 12) {
            
            const classification = extractClassificationSystem(sentence.text);
            if (classification) {
                const options = generateCompleteClassificationOptions(classification);
                
                if (options.length >= 4 && options.includes(classification.system)) {
                    classifications.push({
                        question: `What classification system includes ${classification.items.join(', ')}?`,
                        options: options,
                        correctAnswer: classification.system,
                        explanation: `The classification system includes categories like ${classification.items.join(', ')}`,
                        page: sentence.page,
                        source: sentence.text,
                        type: 'classification'
                    });
                }
            }
        }
    });
    
    return classifications;
}

// Enhanced extraction helper functions
function extractCompleteTerm(text) {
    const words = text.trim().split(/\s+/);
    const meaningfulWords = words.filter(word => {
        const cleanWord = cleanText(word);
        return cleanWord.length > 3 && 
               !['the', 'a', 'an', 'this', 'that', 'these', 'those', 'concept'].includes(cleanWord.toLowerCase());
    });
    
    return meaningfulWords.length > 0 ? cleanText(meaningfulWords[0]) : null;
}

function extractCompleteDefinition(text) {
    let definition = cleanText(text.replace(/[.,;:]$/, ''));
    // Ensure definition is complete and meaningful
    if (definition.split(' ').length < 4) return null;
    return definition;
}

function extractMainConcept(text) {
    const words = text.split(/\s+/);
    for (let i = 0; i < words.length; i++) {
        const word = cleanText(words[i]);
        if (word.length > 5 && /^[A-Z]/.test(word) && !isCommonWord(word)) {
            return word;
        }
    }
    return null;
}

function extractConceptContext(text) {
    // Extract a meaningful context snippet (first 8-10 words)
    const words = text.split(/\s+/).slice(0, 10);
    return words.join(' ') + (text.split(' ').length > 10 ? '...' : '');
}

function extractExampleConcept(text) {
    // Look for the concept being exemplified
    const beforeExample = text.split(/for example|for instance|such as|including/i)[0];
    const words = beforeExample.split(/\s+/);
    
    for (let i = words.length - 1; i >= 0; i--) {
        const word = cleanText(words[i]);
        if (word.length > 4 && /^[A-Z]/.test(word) && !isCommonWord(word)) {
            return word;
        }
    }
    return 'Classification'; // Default fallback
}

function extractExampleItems(text) {
    const items = [];
    const afterExample = text.split(/for example|for instance|such as|including/i)[1];
    if (afterExample) {
        // Extract capitalized words (likely proper nouns or specific terms)
        const matches = afterExample.match(/\b[A-Z][a-z]+\b/g) || [];
        items.push(...matches.slice(0, 3)); // Take up to 3 examples
    }
    return items.length > 0 ? items : ['specific categories'];
}

function extractProcessConcept(text) {
    const words = text.split(/\s+/);
    for (let i = 0; i < words.length; i++) {
        if (words[i].toLowerCase() === 'process' && i > 0) {
            const concept = cleanText(words[i-1]);
            return concept.length > 4 ? concept : 'Classification';
        }
    }
    return 'Classification';
}

function extractClassificationSystem(text) {
    const words = text.split(/\s+/);
    const items = [];
    let system = 'Biological Classification';
    
    // Extract classification items
    const matches = text.match(/\b[A-Z][a-z]+\b/g) || [];
    for (const match of matches) {
        if (match.length > 4 && !isCommonWord(match)) {
            items.push(match);
            if (items.length >= 2) break;
        }
    }
    
    // Determine the classification system
    if (text.toLowerCase().includes('kingdom') || text.toLowerCase().includes('species')) {
        system = 'Taxonomic Classification';
    } else if (text.toLowerCase().includes('category') || text.toLowerCase().includes('type')) {
        system = 'Categorical Classification';
    }
    
    return items.length >= 2 ? { system, items } : null;
}

// Enhanced option generation without hints
function generateCompleteDefinitionOptions(correctTerm) {
    const options = [correctTerm];
    const allTerms = getAllMeaningfulTerms().filter(term => 
        term !== correctTerm && 
        term.length > 3 && 
        !isAdverb(term)
    );
    
    // Add meaningful, related terms
    while (options.length < 4 && allTerms.length > 0) {
        const randomTerm = allTerms[Math.floor(Math.random() * allTerms.length)];
        if (!options.includes(randomTerm)) {
            options.push(randomTerm);
            allTerms.splice(allTerms.indexOf(randomTerm), 1);
        }
    }
    
    // Fill with substantial alternatives
    const substantialTerms = ['Methodology', 'Framework', 'Paradigm', 'Doctrine', 'Discipline', 'System'];
    while (options.length < 4) {
        const substantialTerm = substantialTerms[options.length - 1] || `Concept ${options.length}`;
        if (!options.includes(substantialTerm) && !isAdverb(substantialTerm)) {
            options.push(substantialTerm);
        }
    }
    
    return options;
}

function generateCompleteConceptOptions(correctConcept) {
    const options = [correctConcept];
    const allConcepts = getAllMeaningfulTerms().filter(concept => 
        concept !== correctConcept && 
        concept.length > 4 &&
        !isAdverb(concept)
    );
    
    while (options.length < 4 && allConcepts.length > 0) {
        const randomConcept = allConcepts[Math.floor(Math.random() * allConcepts.length)];
        if (!options.includes(randomConcept)) {
            options.push(randomConcept);
            allConcepts.splice(allConcepts.indexOf(randomConcept), 1);
        }
    }
    
    const substantialConcepts = ['Theoretical Framework', 'Scientific Principle', 'Fundamental Theory', 'Core Concept'];
    while (options.length < 4) {
        const substantialConcept = substantialConcepts[options.length - 1] || `Principle ${options.length}`;
        if (!options.includes(substantialConcept) && !isAdverb(substantialConcept)) {
            options.push(substantialConcept);
        }
    }
    
    return options;
}

function generateCompleteExampleOptions(correctConcept) {
    const options = [correctConcept];
    const allConcepts = getAllMeaningfulTerms().filter(concept => 
        concept !== correctConcept && 
        concept.length > 4 &&
        !isAdverb(concept)
    );
    
    while (options.length < 4 && allConcepts.length > 0) {
        const randomConcept = allConcepts[Math.floor(Math.random() * allConcepts.length)];
        if (!options.includes(randomConcept)) {
            options.push(randomConcept);
            allConcepts.splice(allConcepts.indexOf(randomConcept), 1);
        }
    }
    
    const systemConcepts = ['Taxonomic System', 'Classification Method', 'Categorical Framework', 'Organizational Structure'];
    while (options.length < 4) {
        const systemConcept = systemConcepts[options.length - 1] || `System ${options.length}`;
        if (!options.includes(systemConcept) && !isAdverb(systemConcept)) {
            options.push(systemConcept);
        }
    }
    
    return options;
}

function generateCompleteProcessOptions(correctProcess) {
    const options = [correctProcess];
    const allProcesses = getAllMeaningfulTerms().filter(process => 
        process !== correctProcess && 
        process.length > 4 &&
        !isAdverb(process)
    );
    
    while (options.length < 4 && allProcesses.length > 0) {
        const randomProcess = allProcesses[Math.floor(Math.random() * allProcesses.length)];
        if (!options.includes(randomProcess)) {
            options.push(randomProcess);
            allProcesses.splice(allProcesses.indexOf(randomProcess), 1);
        }
    }
    
    const processTypes = ['Analysis Method', 'Identification Process', 'Categorization System', 'Classification Technique'];
    while (options.length < 4) {
        const processType = processTypes[options.length - 1] || `Method ${options.length}`;
        if (!options.includes(processType) && !isAdverb(processType)) {
            options.push(processType);
        }
    }
    
    return options;
}

function generateCompleteClassificationOptions(classification) {
    const options = [classification.system];
    const allSystems = ['Biological Taxonomy', 'Scientific Classification', 'Systematic Categorization', 'Hierarchical Organization'];
    
    // Remove the correct answer from available systems
    const availableSystems = allSystems.filter(sys => sys !== classification.system);
    
    while (options.length < 4 && availableSystems.length > 0) {
        const randomSystem = availableSystems[Math.floor(Math.random() * availableSystems.length)];
        if (!options.includes(randomSystem)) {
            options.push(randomSystem);
            availableSystems.splice(availableSystems.indexOf(randomSystem), 1);
        }
    }
    
    // Fill remaining slots
    const additionalSystems = ['Functional Classification', 'Structural Organization', 'Thematic Grouping'];
    while (options.length < 4) {
        const additionalSystem = additionalSystems[options.length - 4] || `Classification ${options.length}`;
        if (!options.includes(additionalSystem) && !isAdverb(additionalSystem)) {
            options.push(additionalSystem);
        }
    }
    
    return options;
}

// Utility functions
function getAllCompleteSentences() {
    const sentences = [];
    state.extractedContent.forEach(content => {
        const contentSentences = content.text.split(/[.!?]+/).filter(s => 
            s.trim().length > 25 && // Longer sentences for complete content
            s.split(' ').length > 8 // Minimum word count
        );
        contentSentences.forEach(sentence => {
            sentences.push({
                text: cleanText(sentence.trim()),
                page: content.page
            });
        });
    });
    return sentences;
}

function getAllMeaningfulTerms() {
    const terms = new Set();
    state.extractedContent.forEach(content => {
        const words = content.text.match(/\b[A-Z][a-z]{3,}\b/g) || [];
        words.forEach(word => {
            const cleanWord = cleanText(word);
            if (cleanWord.length > 3 && 
                !isCommonWord(cleanWord) && 
                !isAdverb(cleanWord) &&
                !['This', 'That', 'These', 'Those', 'There', 'Here'].includes(cleanWord)) {
                terms.add(cleanWord);
            }
        });
    });
    return Array.from(terms);
}

function isCommonWord(word) {
    const commonWords = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'your', 'with', 'have', 'this', 'that', 'from'];
    return commonWords.includes(word.toLowerCase());
}

function isAdverb(word) {
    const commonAdverbs = ['very', 'really', 'quite', 'rather', 'somewhat', 'extremely', 'highly', 'fully', 'partially', 'completely'];
    return commonAdverbs.includes(word.toLowerCase());
}

function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}

function cleanText(text) {
    if (!text) return '';
    return text
        .replace(/[-–—]/g, ' ')
        .replace(/[^\w\s]/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}