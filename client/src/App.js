import React, { useEffect, useMemo, useState } from 'react';
import './App.css';

const HISTORY_STORAGE_KEY = 'ielts-task2-score-history';

const CRITERIA = [
  {
    key: 'task_response',
    shortName: 'TR',
    title: 'Task Response',
    description: 'Task achievement, position, support, and development',
  },
  {
    key: 'coherence_cohesion',
    shortName: 'CC',
    title: 'Coherence and Cohesion',
    description: 'Structure, paragraphing, progression, and linking',
  },
  {
    key: 'lexical_resource',
    shortName: 'LR',
    title: 'Lexical Resource',
    description: 'Vocabulary range, precision, spelling, and word choice',
  },
  {
    key: 'grammar_range_accuracy',
    shortName: 'GRA',
    title: 'Grammatical Range and Accuracy',
    description: 'Sentence range, grammar control, and punctuation',
  },
];

const emptyScores = {
  task_response: 0,
  coherence_cohesion: 0,
  lexical_resource: 0,
  grammar_range_accuracy: 0,
};

const initialResults = {
  overall_band: 0,
  criteria_scores: emptyScores,
  raw_scores: emptyScores,
  word_count: 0,
  suggestions: [],
  model_info: null,
};

const getWordCount = (value) => {
  const matches = value.trim().match(/[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+/g);
  return matches ? matches.length : 0;
};

const getParagraphCount = (value) => {
  return value.trim().split(/\n\s*\n/).filter(Boolean).length;
};

const formatRecordTime = (value) => {
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
};

const getAverageRawScore = (rawScores) => {
  const values = CRITERIA.map((criterion) => Number(rawScores?.[criterion.key] || 0));
  const activeValues = values.filter((value) => value > 0);
  if (!activeValues.length) {
    return '0.00';
  }
  return (activeValues.reduce((sum, value) => sum + value, 0) / activeValues.length).toFixed(2);
};

const renderSuggestion = (item) => {
  if (typeof item === 'string') {
    return item;
  }
  return item?.message || 'No suggestion text available.';
};

const HistoryPanel = ({ history, onClearHistory }) => {
  const [query, setQuery] = useState('');

  const filteredHistory = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return history;
    }

    return history.filter((record) => {
      const searchableText = `${record.question} ${record.essay_preview} ${record.overall_band}`.toLowerCase();
      return searchableText.includes(normalizedQuery);
    });
  }, [history, query]);

  const averageBand = history.length
    ? (history.reduce((sum, record) => sum + record.overall_band, 0) / history.length).toFixed(1)
    : '0.0';

  return (
    <section className="history-panel">
      <div className="history-header">
        <div>
          <span className="eyebrow">History</span>
          <h2>Recent Scores</h2>
          <p>{history.length} records | Average band {averageBand}</p>
        </div>
        <button className="history-clear-button" type="button" onClick={onClearHistory} disabled={!history.length}>
          Clear
        </button>
      </div>

      <input
        className="history-search"
        type="search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search question or essay keyword..."
      />

      <div className="history-list">
        {filteredHistory.length === 0 ? (
          <div className="history-empty">No matching history records.</div>
        ) : (
          filteredHistory.map((record) => (
            <article className="history-record" key={record.id}>
              <div>
                <strong>Band {record.overall_band.toFixed(1)}</strong>
                <span>{formatRecordTime(record.created_at)} | {record.word_count} words</span>
              </div>
              <p>{record.question || record.essay_preview || 'Untitled essay'}</p>
            </article>
          ))
        )}
      </div>
    </section>
  );
};

const EssayAnalyzer = () => {
  const [question, setQuestion] = useState('');
  const [essay, setEssay] = useState('');
  const [analysisResults, setAnalysisResults] = useState(initialResults);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [openPanels, setOpenPanels] = useState({ feedback: true });
  const [scoreHistory, setScoreHistory] = useState([]);

  useEffect(() => {
    try {
      const savedHistory = JSON.parse(localStorage.getItem(HISTORY_STORAGE_KEY)) || [];
      setScoreHistory(savedHistory);
    } catch (storageError) {
      console.error('Failed to load score history:', storageError);
      setScoreHistory([]);
    }
  }, []);

  const essayStats = useMemo(() => {
    const words = getWordCount(essay);
    const paragraphs = getParagraphCount(essay);
    const target = 250;
    return {
      words,
      paragraphs,
      target,
      isEnough: words >= target,
      isLong: words > target + 120,
    };
  }, [essay]);

  const feedback = useMemo(() => {
    const suggestions = analysisResults.suggestions || [];
    if (!suggestions.length) {
      return ['Run a prediction to generate feedback.'];
    }

    return suggestions;
  }, [analysisResults]);

  const canAnalyze = question.trim() !== '' && essay.trim() !== '' && !isLoading;

  const saveScoreHistory = (results) => {
    const scoreRecord = {
      id: Date.now(),
      created_at: new Date().toISOString(),
      overall_band: Number(results.overall_band || 0),
      word_count: Number(results.word_count || essayStats.words || 0),
      question: question.trim().slice(0, 140),
      essay_preview: essay.trim().slice(0, 180),
    };

    setScoreHistory((currentHistory) => {
      const nextHistory = [scoreRecord, ...currentHistory].slice(0, 40);
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(nextHistory));
      return nextHistory;
    });
  };

  const handleClearHistory = () => {
    setScoreHistory([]);
    localStorage.removeItem(HISTORY_STORAGE_KEY);
  };

  const handleRunButtonClick = async () => {
    setIsLoading(true);
    setError('');
    setCopied(false);

    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, essay }),
      });

      const results = await response.json();
      if (!response.ok) {
        throw new Error(results.error || 'Failed to analyze the essay.');
      }

      setAnalysisResults(results);
      saveScoreHistory(results);
    } catch (requestError) {
      console.error('Analysis failed:', requestError);
      setError(requestError.message || 'Failed to analyze the essay. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setQuestion('');
    setEssay('');
    setError('');
    setCopied(false);
    setAnalysisResults(initialResults);
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setEssay(text);
      setError('');
    } catch (clipboardError) {
      setError('Clipboard access failed. Please paste manually.');
    }
  };

  const handleCopyReport = async () => {
    const report = [
      'IELTS Writing Task 2 Report',
      `Overall Band: ${analysisResults.overall_band || 0}/9`,
      `Average Raw Score: ${getAverageRawScore(analysisResults.raw_scores)}/9`,
      `Word Count: ${analysisResults.word_count || essayStats.words}`,
      '',
      'Criteria Scores:',
      ...CRITERIA.map((criterion) => (
        `${criterion.title}: ${analysisResults.criteria_scores?.[criterion.key] || 0}/9`
      )),
      '',
      'Suggestions:',
      ...(analysisResults.suggestions || []).map((item) => `${item.title}: ${renderSuggestion(item)}`),
    ].join('\n');

    await navigator.clipboard.writeText(report);
    setCopied(true);
  };

  const togglePanel = (key) => {
    setOpenPanels((current) => ({ ...current, [key]: !current[key] }));
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <div className="logo-mark">I</div>
          <div>
            <h1>IELTS Writing Task 2 Predictor</h1>
            <p>Task 2 essay band prediction and rubric feedback</p>
          </div>
        </div>

        <div className="task-badge" aria-label="Application scope">TASK 2</div>
      </header>

      <main className="workspace-grid">
        <section className="panel left-panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Input</span>
              <h2>Essay Draft</h2>
            </div>
            <div className={essayStats.isEnough ? 'word-status good' : 'word-status warning'}>
              {essayStats.words}/{essayStats.target}
            </div>
          </div>

          <label className="field-group">
            <span>Question</span>
            <em>Paste the IELTS Writing Task 2 question as plain text.</em>
            <textarea
              className="question-input"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Some people believe universities should focus on employment skills. To what extent do you agree or disagree?"
            />
          </label>

          <label className="field-group essay-field">
            <span>Candidate Essay</span>
            <textarea
              value={essay}
              onChange={(event) => setEssay(event.target.value)}
              placeholder="Write or paste the candidate essay here."
            />
          </label>

          <div className="input-tools">
            <div className="stats-row">
              <span className={essayStats.isEnough ? 'stat-chip good' : 'stat-chip warning'}>
                {essayStats.words} words
              </span>
              <span className="stat-chip">{essayStats.paragraphs} paragraphs</span>
              <span className={essayStats.isLong ? 'stat-chip warning' : 'stat-chip'}>
                {essayStats.isLong ? 'Long draft' : 'Length check'}
              </span>
            </div>
            <div className="quick-actions">
              <button type="button" onClick={handlePaste}>Paste</button>
              <button type="button" onClick={handleClear}>Clear</button>
            </div>
          </div>
        </section>

        <section className="center-action" aria-label="Submit score">
          <button className="score-button" onClick={handleRunButtonClick} disabled={!canAnalyze}>
            {isLoading ? <span className="spinner" /> : <span className="button-arrow">&gt;</span>}
            {isLoading ? 'Scoring...' : 'Score Essay'}
          </button>
          <p>Uses the unified Task 2 scoring endpoint.</p>
          {error && <div className="error-message">{error}</div>}
        </section>

        <section className="panel report-panel">
          <div className="report-hero">
            <div>
              <span className="eyebrow">Report</span>
              <h2>Overall Band</h2>
            </div>
            <strong>{analysisResults.overall_band || 0}</strong>
          </div>

          <div className="criteria-grid">
            {CRITERIA.map((criterion) => (
              <article className="criterion-card" key={criterion.key}>
                <div>
                  <span>{criterion.shortName}</span>
                  <strong>{Number(analysisResults.criteria_scores?.[criterion.key] || 0).toFixed(1)}</strong>
                </div>
                <h3>{criterion.title}</h3>
                <p>{criterion.description}</p>
              </article>
            ))}
          </div>

          <div className="report-meta">
            <span>Raw average {getAverageRawScore(analysisResults.raw_scores)}/9</span>
            <span>{analysisResults.word_count || essayStats.words} words</span>
            <span>{analysisResults.model_info?.target || 'ielts_task2'}</span>
          </div>

          <button className="copy-button" onClick={handleCopyReport} disabled={!analysisResults.overall_band}>
            {copied ? 'Copied' : 'Copy Report'}
          </button>

          <div className="accordion-list">
            <div className="accordion-item">
              <button type="button" onClick={() => togglePanel('feedback')}>
                Feedback
                <span>{openPanels.feedback ? '-' : '+'}</span>
              </button>
              {openPanels.feedback && (
                <ul>
                  {feedback.map((item, index) => (
                    <li key={index}>{renderSuggestion(item)}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <HistoryPanel history={scoreHistory} onClearHistory={handleClearHistory} />
        </section>
      </main>
    </div>
  );
};

export default EssayAnalyzer;
