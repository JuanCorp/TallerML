## Including the required R packages.
#packages <- c('shiny', 'shinyjs')
#if (length(setdiff(packages, rownames(installed.packages()))) > 0) {
#  install.packages(setdiff(packages, rownames(installed.packages())))  
#}

library(shiny)
library(shinyjs)

shinyUI(fluidPage(
  conditionalPanel(condition='!output.json',
                   tags$head(tags$script(src = "script.js"),
                   			 tags$script(src = "google-analytics.js"),
                         tags$style(HTML("a { font-weight: bold; } .shiny-output-error-validation { color: red; } .shiny-progress .progress { background-color: #ff00ff; } .fa-info { margin: 0 0 0 10px; cursor: pointer; font-size: 15px; color: #808080; } .fa-headphones { margin: 0 5px 0 2px; } .average-pitch { font-size: 18px; } .detail-summary { font-size: 16px; } .detail-summary .detail-header { font-size: 18px; margin: 0 0 10px 0; } .detail-summary span { font-weight: bold; }"))
                   ),
                   titlePanel('Cual es tu genero segun tu voz?'),
                   div(style='margin: 30px 0 0 0;'),
                   mainPanel(width = '100%',
                             useShinyjs(),
                             h4(id='main', 'Sube un archivo .WAV or escribe un url de ', a(href='http://vocaroo.com', target='_blank', 'vocaroo.com'), ' o ', a(href='http://clyp.it', target='_blank', 'clyp.it'), ' para detectar el genero.'),
                             div(style='margin: 20px 0 0 0;'),
                             
                             inputPanel(
                               div(id='uploadDiv', class='', style='height: 120px; border-right: 1px solid #ccc;',
                                   fileInput('file1', 'Subir Archivo WAV.', accept = c('audio/wav'), width = '100%')
                               ),
                               div(id='urlDiv', class='',
                                   strong('Url (vocaroo o clyp.it)'),
                                   textInput('url', NULL, width = '100%'),
                                   actionButton('btnUrl', 'Cargar Url', class='btn-primary', icon=icon('cloud'))
                               )
                             ),
                             
                             div(style='margin: 20px 0 0 0;'),
                             div(id='result', style='font-size: 22px;', htmlOutput('content')),
                             div(style='margin: 20px 0 0 0;'),
                             
                             conditionalPanel(condition='output.content != null && output.content.indexOf("Please Enter") == -1',
                               tabsetPanel(id='graphs',
                                 tabPanel('Frequency Graph', plotOutput("graph1", width=1000, height=500)),
                                 tabPanel('Spectrogram', plotOutput("graph2", width=1000, height=500))
                               ),
                               div(style='margin: 20px 0 0 0;')
                             ),

                             h4('Truquitos'),
                             p('-  La entonación y tonos son factores importantes en la clasificacion hombre/mujer.'),
                             p('- Voces clasificadas como masculinas suelen ser monotonas(tono bajo).'),
                             p('- Voces clasificadas como femeninas tienden a ser de tono alto y de cambios de  frequencia alta.'),
                             p('- Voces clasificadas como femeninas suelen aumentar en tono al final de una oración.'),
                             div(style='margin: 20px 0 0 0;'),
                             
                             
                               span(style='font-style: italic;', 'Forkeado de https://github.com/primaryobjects/voice-gender')
                   ))
))