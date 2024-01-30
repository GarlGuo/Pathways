import React from 'react';
import "react-responsive-carousel/lib/styles/carousel.min.css"; // requires a loader
import { Carousel } from 'react-responsive-carousel';
import tracy from './images/picoftracy.png';
import jason from './images/jason.png';
import megan from './images/megan.png';
import opening_quotes from './images/opening_quotes.svg';
import closing_quotes from './images/closing_quotes.svg';
import './Personas.css';

const Persona = ({ image, name, title, quote }) => {
  return (
    <div className="persona">
      <img src={opening_quotes} className="opening_quotes" />
      <p>{quote}</p>
      <img src={closing_quotes} className="closing_quotes" />
      <div class="personaLabel">
        <img class="carouselImg" src={image} />
        <div class="personaText">
          <h3>{name}</h3>
          <h4>{title}</h4>
        </div>
      </div>
    </div>
  );
}

const Personas = props => {
  return (
    <div>
      <Carousel showArrows={true} autoPlay infiniteLoop useKeyboardArrows showThumbs={false}>
        <Persona image={tracy} name="Tracy M." title="Transfer Student" quote="As a transfer, I had way less time and people to help me figure out what classes to take and discover my college path." />
        <Persona image={jason} name="Jason L." title="Freshman" quote="I don't know exactly what I want to do when I graduate but I have some ideas of what I'm interested in. I would like to explore different options out there." />
        <Persona image={megan} name="Megan G." title="Junior" quote="I'm thinking a lot about what I want to do after I graduate. I hope I can find classes that inspire my career goals." />
      </Carousel>
    </div >
  );
}

export default Personas;
