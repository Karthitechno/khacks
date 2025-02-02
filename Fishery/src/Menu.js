import React from "react";
import Accordion from './components/Accordion'

const Menu = () => {
    const accordionData = [
        {
          title: 'Maps',
          content: <ul className="menu-list">
              <li>Map 1</li>
              <li>Map 2</li>
          </ul>
        },
        {
            title: 'Report',
            content: <ul className="menu-list">
                <li>View</li>
                <li>Generate</li>
            </ul>
          }
    ];
    return (
        <div className='menu'>
            {accordionData.map(({ title, content },i) => (
                <Accordion key={i} title={title} content={content} />
            ))}
        </div>
    );
}

export default Menu