import App, { Container } from "next/app";
import React, { Fragment } from "react";

class SportscardApp extends App {
  render() {
    const { Component, pageProps } = this.props;
    return (
      <Container>
        <Component {...pageProps} />
      </Container>
    );
  }
}

export default SportscardApp;
