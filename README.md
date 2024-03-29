# gaimeface

-Kishore Venkateshan

-Kristin Jordan

-Mobeen Tariq

-Seunghee Yoon 

-GaimeFace uses a character story to develop an AI football fan that generates emotional reactions. The reactions of the character are generated on a play-by-play basis using animations to visualize the generated emotions through facial expressions. This model aims to mimic human emotions that a person would have watching a football game if he or she were to have similar background story as our developed character. 

-Affective computing has been a large interest in the gaming industry. Incorporating more personalized experiences helps to gain the interest of players, as the experience seems more realistic. As stated by Georgios N. Yannakakis, “the holy grail of game design, that is player experience, can be improved and tailored to each player but also augmented via richer and more affective-based interaction.” Our project not only addresses making animated characters with more personalised expressions, it analyzes and derives values for a person’s gaming experience in real time. This information can also be implemented into games for a more affect-based game. Supporting articles prove that “affect-based game interaction can drive players in particular emotional patterns which, in turn, can enhance game-based training and educational activities“ (McQuiggan, Robison, & Lester, 2010), (McQuiggan & Lester, 2009), (Yannakakis G. N., et al., 2010). Consequently, our project has the potential to be used for various applications. These include but are not limited to: more complex animated game characters, affect-based game creation, more emotive animated movie/TV extras, etc. There is currently no existing model for emotional synthesis or modeling in reaction to football games. With our project being the first, the necessities for each subdivision were analysed thoroughly to give us our current model. This paper will review the thought process, contributing factors, and final result of our project. 

-There are 4 key subdivisions to our solution that were assigned to four members of the team. The subsections are: character sketch (Yoon), character goals and desires (Kristin), emotion generation (Mobeen), and character animation (Kishore). Character sketch focuses on reading and understanding the given story, building a past event structure and creating a memory bank. Using that information character goals and desires is created, defining the utility of events based on the memories of the character. The goals will be used to generate an emotion and the intensity of the emotion for the character. Character animation portrays this emotion and intensity on top of a digital double model offered by Eisko. A measure of success for GaimeFace will be to compare the outputs of the animated character to responses of people who have similar background stories either by watching them react to the exact same plays.

-The character sketch is a combination of parameters, we call descriptors, that describe a sports fan. The project’s initial input is a story written by the fan about themself. Using CoreNLP and Watson’s natural language understanding we derive values for each variable which will ultimately drive the emotions and intensities. The values for each descriptor are on a 0-1 scale and will be used in the other section functions. The descriptors are based on questions we believe will best describe the fans relationship with football and the teams playing. They are used throughout our project as subjective factors to make the character personalized to each fan’s story. The descriptors answer the following questions: 

-Football_experience: How much experience do you have with football?

-Positive_development: Has any significant development happened to your team that you feel positively about? 

-Negative_development: Has any significant development happened to your team that you feel negatively about?

-Reaction_intensity: How intense are your reactions to football related events? 

-Present_or_past: Are your feelings regarding a game based on the present game or the teams history? (0 for present - 1 for history)

-Coping_for_team: Are there any events regarding the team that may help you cope?

-Coping_ability: How good are you at coping?

-Game_type: What type of game would you like to see (blowout-1, fair game-0.5, doesn’t matter-0)?
