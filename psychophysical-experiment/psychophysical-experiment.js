/*
 * Snake Illusion Experiment - Generic Template
 * 
 * Template version for public use
 * Replace imageMapping and imageParameters with your own stimuli
 * 
 * For detailed instructions, see README.md
 */

//Initialize jsPsych
var jsPsych = initJsPsych({
    on_finish: function() {
        enrichData(); 
    }
});

// Global timer variable to stop the countdown
var countdownInterval = null;

// Initializes countdown timer at the beginning of each trial
function startCountdown(duration) {
    clearInterval(countdownInterval);
    var timer = duration;
    var countdownDiv = document.getElementById('countdown');
    if (countdownDiv) {
        countdownDiv.textContent = "Time left: " + timer + "s";
    }
    countdownInterval = setInterval(function() {
        timer--;
        if (countdownDiv) {
            countdownDiv.textContent = "Time left: " + timer + "s";
        }
        if (timer <= 0) {
            clearInterval(countdownInterval);
        }
    }, 1000);
}

// TEMPLATE - Replace with your own stimuli
var imageMapping = {
  'img1': 'stimulus_001.png',
  'img2': 'stimulus_002.png',
  'img3': 'stimulus_003.png',
  'img4': 'stimulus_004.png',
  'img5': 'stimulus_005.png',
  'img6': 'stimulus_006.png'
  // Add your stimuli here
}; 

// TEMPLATE - Configure your stimulus parameters
var imageParameters = {
  'img1': { param1: 'type_A', param2: 'pattern_1', param3: 'variation_low' },
  'img2': { param1: 'type_A', param2: 'pattern_2', param3: 'variation_high' },
  'img3': { param1: 'type_B', param2: 'pattern_1', param3: 'variation_low' },
  'img4': { param1: 'type_B', param2: 'pattern_2', param3: 'variation_high' },
  'img5': { param1: 'type_A', param2: 'pattern_3', param3: 'variation_mixed' },
  'img6': { param1: 'type_B', param2: 'pattern_3', param3: 'variation_mixed' }
  // Configure your parameters here
};

// Get the simplified image names to shuffle
var simpleNames = Object.keys(imageMapping);
var images = jsPsych.randomization.shuffle(simpleNames.slice());

//Define list of images to preload before the experiment
var imagesToPreload = [
    ...Object.values(imageMapping),
    'practice_example.png', 
    'Inward.png', 
    'Outward.png', 
    'snake_icon.png'
];

// Load all images into memory before the experiment starts
var preload = {
    type: jsPsychPreload,
    images: imagesToPreload,
    message: 'Loading experiment images...',
    show_progress_bar: true,
    continue_after_error: true,
    error_message: 'An error occurred while loading. The experiment will continue, but some images might not display correctly.'
};

// Function to display the countdown timer on screen
var addFixedTimer = {
    type: jsPsychCallFunction,
    func: () => {
        var countdownDiv = document.createElement('div');
        countdownDiv.id = 'countdown';
        countdownDiv.style.position = 'fixed';
        countdownDiv.style.top = '20px';
        countdownDiv.style.right = '20px';
        countdownDiv.style.fontSize = '30px';
        countdownDiv.style.fontFamily = 'Arial, sans-serif';
        countdownDiv.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
        countdownDiv.style.padding = '10px 15px';
        countdownDiv.style.borderRadius = '10px';
        countdownDiv.style.zIndex = '1000';
        countdownDiv.innerText = "Time left: 6s";
        document.body.appendChild(countdownDiv);
    }
};

// Function to remove the countdown timer from the screen
var removeFixedTimer = {
    type: jsPsychCallFunction,
    func: () => {
        clearInterval(countdownInterval);
        var countdownDiv = document.getElementById('countdown');
        if (countdownDiv) {
            countdownDiv.remove();
        }
    }
};

// Function to add a progress bar with corrected position and displayed information
var addProgressBar = {
    type: jsPsychCallFunction,
    func: function() {
        // Create progress bar container if it doesn't exist
        if (!document.getElementById('progress-container')) {
            var container = document.createElement('div');
            container.id = 'progress-container';
            container.style.position = 'fixed';
            container.style.top = '10px';  // Changed from bottom to top
            container.style.left = '50%';
            container.style.transform = 'translateX(-50%)';
            container.style.width = '60%';  // Made smaller
            container.style.maxWidth = '400px';
            container.style.backgroundColor = 'rgba(240, 240, 240, 0.9)';
            container.style.borderRadius = '10px';
            container.style.padding = '5px 8px';
            container.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
            container.style.zIndex = '999';  // Lower z-index so countdown timer is above it
            
            var progressText = document.createElement('div');
            progressText.id = 'progress-text';
            progressText.style.textAlign = 'center';
            progressText.style.fontSize = '12px';  // Smaller text
            progressText.style.fontFamily = 'Arial, sans-serif';
            progressText.style.color = '#333';
            progressText.style.marginBottom = '3px';
            progressText.textContent = 'Progress: 0%';  // Only show percentage
            
            var progressBar = document.createElement('div');
            progressBar.style.width = '100%';
            progressBar.style.backgroundColor = '#ddd';
            progressBar.style.height = '8px';  // Thinner bar
            progressBar.style.borderRadius = '4px';
            progressBar.style.overflow = 'hidden';
            
            var progressFill = document.createElement('div');
            progressFill.id = 'progress-fill';
            progressFill.style.width = '0%';
            progressFill.style.backgroundColor = '#4CAF50';
            progressFill.style.height = '100%';
            progressFill.style.transition = 'width 0.3s ease';
            
            progressBar.appendChild(progressFill);
            container.appendChild(progressText);
            container.appendChild(progressBar);
            document.body.appendChild(container);
        }
    }
};

// Initialize progress counter
var initializeProgress = {
    type: jsPsychCallFunction,
    func: function() {
        window.completedTrials = 0;
        window.totalTrials = images.length;
    }
};

// Update progress function - only percentages
var updateProgressBar = {
    type: jsPsychCallFunction,
    func: function() {
        // Make sure counter is initialized
        if (typeof window.completedTrials === 'undefined') {
            window.completedTrials = 0;
            window.totalTrials = images.length;
        }
        
        // Update counter before showing next image
        window.completedTrials += 1;
        
        // Calculate progress percentage
        var progressPercent = Math.min(Math.round((window.completedTrials / window.totalTrials) * 100), 100);
        
        // Update progress bar
        var progressFill = document.getElementById('progress-fill');
        var progressText = document.getElementById('progress-text');
        
        if (progressFill && progressText) {
            progressFill.style.width = progressPercent + '%';
            progressText.textContent = 'Progress: ' + progressPercent + '%';
        }
    }
};

// Function to remove the progress bar at the end of the experiment
var removeProgressBar = {
    type: jsPsychCallFunction,
    func: function() {
        var container = document.getElementById('progress-container');
        if (container) {
            container.remove();
        }
    }
};

// Fade-in effect for the welcome screen
var fadeInWelcome = {
    type: jsPsychCallFunction,
    func: function() {
        setTimeout(function() {
            var container = document.getElementById('welcome-container');
            if (container) {
                container.style.opacity = 1;
            }
        }, 50);
    }
};

// Function to change the background on the welcome screen
var setWelcomeBackground = {
    type: jsPsychCallFunction,
    func: function() {
        document.body.style.backgroundColor = "#eeeeee"; //  
    }
};

// Function to reset the background to white after the welcome screen
var resetBackground = {
    type: jsPsychCallFunction,
    func: function() {
        document.body.style.backgroundColor = "#ffffff"; // Back to white background
    }
};

// Professional welcome screen – vertically centered
var welcome = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
        <div id="welcome-container" style="
            width: 100%;
            height: 100vh;
            opacity: 0;
            transition: opacity 1.5s ease;
            text-align: center;
            font-family: 'Arial', sans-serif;
            color: #333;
            box-sizing: border-box;
            text-align: center;
            padding-top: 30%;
        ">
            <img src="Snake_cartoon.png" alt="Snake Illusion" style="
                width: 250px;
                margin-bottom: 30px;
            ">
            <h1 style="font-size: 36px; margin-bottom: 20px;">Welcome to the Snake Illusion Experiment</h1>
            <p style="font-size: 20px; max-width: 600px; margin: auto; margin-bottom: 20px; line-height: 1.6;">
                In this experiment, you will view a series of images.<br>
                Each image will appear for <strong>6 seconds</strong>.<br>
                Your task- <strong>Decide quickly: Is the motion inward or outward?</strong>
            </p>
            <div style="font-size: 22px; margin-top: 30px; color: #007ACC; font-weight: bold;">
                Press any key to start
            </div>
        </div>

        <style>
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
                100% { transform: translateY(0px); }
            }
        </style>
    `
};

// Practice trial before the experiment
var practice_start = {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
        <h2>Practice Trial</h2>
        <p>Press the button below to start the practice trial.</p>
    `,
    choices: [
      '<span style="font-weight: bold; color: #007ACC;">Start Practice</span>'
]

};

var practice_trial = {
    timeline: [
        addFixedTimer,     // Displays the countdown box
        {
            type: jsPsychHtmlButtonResponse,
            stimulus: `
                <div style="display: flex; justify-content: center; align-items: center; height: 80vh;">
                    <img src="practice_example.png" style="max-height: 400px; max-width: 90%; object-fit: contain;">
                </div>
            `,
            choices: [
              `<div style="display: flex; flex-direction: column; align-items: center;">
                  <img src="Inward.png" alt="Inward" style="height:60px; margin-bottom:5px;">
                  <span style="font-size: 14px; color: #333;">Inward</span>
              </div>`,
              `<div style="display: flex; flex-direction: column; align-items: center;">
                  <img src="Outward.png" alt="Outward" style="height:60px; margin-bottom:5px;">
                  <span style="font-size: 14px; color: #333;">Outward</span>
              </div>`
            ],
            trial_duration: 6000,
            on_load: function() {
                startCountdown(6);
            },
            on_finish: function(data) {
                if (data.response == null) {
                    alert("You didn't respond in time. In the real experiment, you'll need to choose within the time limit.");
                }
            }
        },
        removeFixedTimer       // Removes the countdown box after the practice trial
    ]
};

var start_real_experiment = {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
        <h2>Practice Completed</h2>
        <p>Press the button below to start the real experiment.</p>
    `,
    choices: [
        '<span style="font-weight: bold; color: #007ACC;">Start Real Experiment</span>'
    ]
};

//  Break after every 4 trials (configurable)
var break_screen = {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
        <h2>Take a short break if needed</h2>
        <p>You've completed a set of trials.</p>
        <p>Feel free to take a short break if you need one.</p>
        <p>Press the button below when you're ready to continue.</p>
    `,
    choices: [
        '<span style="font-weight: bold; color: #007ACC;">Continue </span>'
    ],
    data: { trial_type: "break" }
};

// Creating the illusion trials
var illusion_trials = [];

// Configuration: Change this number to adjust break frequency (set to 0 to disable breaks)
var BREAK_FREQUENCY = 4;

// Adds the trials along with scheduled breaks
images.forEach(function(img, index) {
    // Add the trial
    illusion_trials.push({
        timeline: [
            {
                type: jsPsychCallFunction,
                func: function() {
                    var countdownDiv = document.getElementById('countdown');
                    if (!countdownDiv) {
                        countdownDiv = document.createElement('div');
                        countdownDiv.id = 'countdown';
                        countdownDiv.style.position = 'fixed';
                        countdownDiv.style.top = '20px';
                        countdownDiv.style.right = '20px';
                        countdownDiv.style.fontSize = '30px';
                        countdownDiv.style.fontFamily = 'Arial, sans-serif';
                        countdownDiv.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
                        countdownDiv.style.padding = '10px 15px';
                        countdownDiv.style.borderRadius = '10px';
                        countdownDiv.style.zIndex = '1000';
                        document.body.appendChild(countdownDiv);
                    }
                    countdownDiv.innerText = "Time left: 6s";
                    clearInterval(countdownInterval);
                    var timer = 6;
                    countdownInterval = setInterval(function() {
                        timer--;
                        if (timer >= 0) {
                            countdownDiv.innerText = "Time left: " + timer + "s";
                        }
                        if (timer <= 0) {
                            clearInterval(countdownInterval);
                        }
                    }, 1000);
                }
            },
            {
                type: jsPsychHtmlButtonResponse,
                stimulus: `
                    <div style="display: flex; justify-content: center; align-items: center; height: 80vh;">
                        <img src="${imageMapping[img]}" style="max-height: 400px; max-width: 90%; object-fit: contain;">
                    </div>
                `,
                choices: [
                    `<div style="display: flex; flex-direction: column; align-items: center;">
                        <img src="Inward.png" alt="Inward" style="height:60px; margin-bottom:5px;">
                        <span style="font-size: 14px; color: #333;">Inward</span>
                    </div>`,
                    `<div style="display: flex; flex-direction: column; align-items: center;">
                        <img src="Outward.png" alt="Outward" style="height:60px; margin-bottom:5px;">
                        <span style="font-size: 14px; color: #333;">Outward</span>
                    </div>`
                ],
                trial_duration: 6000,
                response_ends_trial: true,
                data: {
                    illusion_id: index + 1,
                    actual_filename: imageMapping[img],
                    param1: imageParameters[img].param1,
                    param2: imageParameters[img].param2,
                    param3: imageParameters[img].param3
                },
                on_finish: function(data) {
                    clearInterval(countdownInterval);
                    var countdownDiv = document.getElementById('countdown');
                    if (countdownDiv) {
                        countdownDiv.remove();
                    }
                    data.missed_response = (data.response == null);
                    
                    // Only update progress if they responded
                    if (data.response !== null) {
                        // Call update progress function
                        updateProgressBar.func();
                    }
                }
            },
            {
                timeline: [
                    {
                        type: jsPsychHtmlButtonResponse,
                        stimulus: `
                            <div style="background-color: #FFE0B2; height: 70vh; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                                <h3 style="color: #333;">You did not respond in time.<br>Please select an answer:</h3>
                            </div>
                        `,
                        choices: [
                           `<div style="display: flex; flex-direction: column; align-items: center;">
                            <img src="Inward.png" alt="Inward" style="height:60px; margin-bottom:5px;">
                            <span style="font-size: 14px; color: #333;">Inward</span>
                            </div>`,
                            `<div style="display: flex; flex-direction: column; align-items: center;">
                            <img src="Outward.png" alt="Outward" style="height:60px; margin-bottom:5px;">
                            <span style="font-size: 14px; color: #333;">Outward</span>
                            </div>`
                        ],
                        data: {
                            missed_correction: true,
                            actual_filename: imageMapping[img],
                            param1: imageParameters[img].param1,
                            param2: imageParameters[img].param2,
                            param3: imageParameters[img].param3
                        },
                        on_finish: function() {
                            // Update progress after they give a response in the correction screen
                            updateProgressBar.func();
                        }
                    }
                ],
                conditional_function: function() {
                    var last = jsPsych.data.get().last(1).values()[0];
                    return last.missed_response === true;
                }
            }
        ]
    });
    
    // Add break after every BREAK_FREQUENCY trials (but not after the last trial)
    if (BREAK_FREQUENCY > 0 && (index + 1) % BREAK_FREQUENCY === 0 && index < images.length - 1) {
        illusion_trials.push(break_screen);
    }
});

// Completion screen
var completion = {
    type: jsPsychHtmlKeyboardResponse,
    stimulus: `
        <h1>Thank you!</h1>
        <p>Your responses have been recorded.</p>
        <b>Press "Esc", then close this window</b>
    `,
    on_load: function() {
        // Update progress to 100% at the end
        var progressFill = document.getElementById('progress-fill');
        var progressText = document.getElementById('progress-text');
        
        if (progressFill && progressText) {
            progressFill.style.width = '100%';
            progressText.textContent = 'Progress: 100%';
        }
    }
};

// Asks if the participant has already completed the training
var trainingCheck = {
    type: jsPsychHtmlButtonResponse,
    stimulus: `
        <h2>Have you already completed the training?</h2>
        <p>Please choose an option to continue:</p>
    `,
    choices: [
      '<span style="font-weight: bold; color: #007ACC;">This is my first time (I need training)</span>',
      '<span style="font-weight: bold; color: #007ACC;">I already did the training</span>'
    ],

    data: { trial_type: "training_check" }
};


// If the user chose the option – show the practice trial
var conditional_training = {
    timeline: [practice_start].concat(practice_trial.timeline).concat([start_real_experiment]),
    conditional_function: function() {
        var last = jsPsych.data.get().last(1).values()[0];
        return last.response === 0; // Practice trial = 0
    }
};

// Building the final timeline
var timeline = [
    preload,     
    setWelcomeBackground,
    fadeInWelcome,
    welcome,
    resetBackground,
    trainingCheck,           
    conditional_training,    
    initializeProgress,      
    addProgressBar           
];

// Adding the real experiment trials
illusion_trials.forEach(function(trial) {
    timeline.push(trial);
});

// Completion screen
timeline.push(removeProgressBar);  // Removes the progress bar
timeline.push(completion);

// Running the experiment
jsPsych.run(timeline);

// enrichData- Adding important fields
function enrichData() {
    var allData = jsPsych.data.get().filter(function(trial){
        return trial.trial_type === 'html-button-response' && 
               trial.stimulus.indexOf('practice_example.png') === -1 &&
               (trial.actual_filename !== undefined || trial.missed_correction === true);
    });

    allData.each(function(trial) {
        var responseLabel;
        if (trial.response === 0) {
            responseLabel = "Inward";
        } else if (trial.response === 1) {
            responseLabel = "Outward";
        } else {
            responseLabel = "No Response";
        }

        var missed = (trial.response == null) ? "Yes" : "No";

        // Find the simple image name from the full filename if available
        var simpleFilename = null;
        if (trial.actual_filename) {
            simpleFilename = Object.keys(imageMapping).find(key => 
                imageMapping[key] === trial.actual_filename);
        }
        
        // Add enriched data fields
        trial.response_label = responseLabel;
        trial.missed_initial_response = missed;
        
        // The param1, param2, param3 are already included from the trial data
        // but we ensure they're properly labeled for analysis
        if (trial.param1 !== undefined) {
            trial.parameter_1 = trial.param1;
        }
        if (trial.param2 !== undefined) {
            trial.parameter_2 = trial.param2;
        }
        if (trial.param3 !== undefined) {
            trial.parameter_3 = trial.param3;
        }
    });
}